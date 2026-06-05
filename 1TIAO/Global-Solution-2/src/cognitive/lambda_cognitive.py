"""
lambda_cognitive.py — Lambda Handler para geração de boletins HeliOS
HeliOS | Global Solution 2026.1 — FIAP

Handler: lambda_cognitive.lambda_handler
Runtime: Python 3.12
Memory: 256 MB | Timeout: 120s
Trigger: EventBridge (rate 6 hours)

Variáveis de ambiente esperadas:
    SNS_TOPIC_ARN   — ARN do tópico helios-storm-alerts
    S3_BUCKET_NAME  — helios-solar-data
    OPENAI_API_KEY  — chave OpenAI (opcional, usa Bedrock como fallback)
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import boto3

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN",    "arn:aws:sns:us-east-1:065818678123:helios-storm-alerts")
S3_BUCKET     = os.environ.get("S3_BUCKET_NAME",   "helios-solar-data")
DYNAMO_TABLE  = os.environ.get("DYNAMO_TABLE",     "helios-kp-realtime")
AWS_REGION    = "us-east-1"
KP_ALERT_THRESHOLD = 5.0


def get_latest_kp(n=6):
    dynamo = boto3.resource("dynamodb", region_name=AWS_REGION)
    table  = dynamo.Table(DYNAMO_TABLE)
    resp   = table.scan(Limit=50)
    items  = sorted(resp.get("Items", []), key=lambda x: x.get("timestamp", ""), reverse=True)
    return items[:n]


def build_prompt(kp_readings):
    if kp_readings:
        b_values = [float(r.get("b_total_nT", 23000)) for r in kp_readings]
        b_mean   = sum(b_values) / len(b_values)
        b_min    = min(b_values)
        stati    = [r.get("geo_status", "QUIET") for r in kp_readings]
        dominant = max(set(stati), key=stati.count)
        kp_vals  = [float(r.get("kp_proxy", 0)) for r in kp_readings]
        kp_mean  = sum(kp_vals) / len(kp_vals)
    else:
        b_mean, b_min, dominant, kp_mean = 23000, 23000, "QUIET", 0

    return f"""Você é um sistema especialista em meteorologia espacial.
Gere um boletim técnico CONCISO (máximo 250 palavras) em português.

Dados:
- Campo magnético médio: {b_mean:.0f} nT (referência: 23.000 nT)
- Campo mínimo recente: {b_min:.0f} nT
- Status geomagnético: {dominant}
- Kp proxy médio: {kp_mean:.1f}

Formato obrigatório:
## NÍVEL DE RISCO ATUAL
## INFRAESTRUTURAS EM RISCO
## JANELA TEMPORAL
## RECOMENDAÇÕES

Data: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
Sistema: HeliOS v1.0 | FIAP Global Solution 2026"""


def generate_bulletin(prompt, kp_readings):
    # Tentativa 1: OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500, temperature=0.3,
            )
            return resp.choices[0].message.content, "openai"
        except Exception as e:
            print(f"OpenAI error: {e}")

    # Tentativa 2: Bedrock
    try:
        bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}],
        })
        resp = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=body, contentType="application/json", accept="application/json",
        )
        result = json.loads(resp["body"].read())
        return result["content"][0]["text"], "bedrock"
    except Exception as e:
        print(f"Bedrock error: {e}")

    # Fallback: template
    geo = kp_readings[0].get("geo_status", "QUIET") if kp_readings else "QUIET"
    nivel = "EXTREMO" if "STORM" in geo else ("ALTO" if geo == "ACTIVE" else "BAIXO")
    return f"""## NÍVEL DE RISCO ATUAL
{nivel} — Baseado em leituras geomagnéticas recentes.

## INFRAESTRUTURAS EM RISCO
- Satélites LEO, redes elétricas, GPS, comunicações HF

## JANELA TEMPORAL
Próximas 12-24 horas

## RECOMENDAÇÕES
1. Monitorar satélites em órbita baixa
2. Verificar transformadores de alta tensão
3. Alertar operadores de aviação polar
4. Ativar sistemas de navegação redundantes

Sistema: HeliOS v1.0 [TEMPLATE]""", "template"


def lambda_handler(event, context):
    print("HeliOS Cognitive Lambda iniciado")
    t0 = time.time()

    kp_readings = get_latest_kp()
    print(f"Leituras DynamoDB: {len(kp_readings)}")

    prompt = build_prompt(kp_readings)
    bulletin, source = generate_bulletin(prompt, kp_readings)
    print(f"Boletim gerado via: {source}")

    # Determinar alerta
    kp_proxies = [float(r.get("kp_proxy", 0)) for r in kp_readings]
    kp_max = max(kp_proxies) if kp_proxies else 0
    should_alert = kp_max >= KP_ALERT_THRESHOLD

    # SNS
    sns_sent = False
    if should_alert:
        try:
            sns = boto3.client("sns", region_name=AWS_REGION)
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"⚡ HeliOS ALERTA — Risco Geomagnético Elevado | Kp~{kp_max:.1f}",
                Message=bulletin,
            )
            sns_sent = True
            print("SNS alerta enviado")
        except Exception as e:
            print(f"SNS error: {e}")

    # S3
    s3_path = None
    try:
        s3  = boto3.client("s3", region_name=AWS_REGION)
        now = datetime.now(timezone.utc)
        key = f"bulletins/{now.strftime('%Y/%m/%d/%H-%M')}.json"
        s3.put_object(
            Bucket=S3_BUCKET, Key=key,
            Body=json.dumps({"bulletin": bulletin, "source": source,
                             "kp_max": float(kp_max), "sns_sent": sns_sent,
                             "generated_at": now.isoformat()},
                            ensure_ascii=False, indent=2),
            ContentType="application/json",
        )
        s3_path = f"s3://{S3_BUCKET}/{key}"
        print(f"Boletim salvo: {s3_path}")
    except Exception as e:
        print(f"S3 error: {e}")

    result = {
        "statusCode": 200,
        "bulletin_preview": bulletin[:200] + "...",
        "source": source,
        "kp_max": float(kp_max),
        "sns_sent": sns_sent,
        "s3_path": s3_path,
        "duration_ms": int((time.time() - t0) * 1000),
    }
    print(json.dumps(result))
    return result
