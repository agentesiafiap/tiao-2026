"""
bulletin_generator.py — Gerador de Boletins Cognitivos de Meteorologia Espacial
HeliOS | Global Solution 2026.1 — FIAP

═══════════════════════════════════════════════════════════════════
CONCEITO: API COGNITIVA NA ARQUITETURA HeliOS
═══════════════════════════════════════════════════════════════════

Este módulo é o cérebro analítico do HeliOS. Ele recebe dados de
todos os sensores e modelos de ML e sintetiza um boletim técnico
em linguagem natural usando um LLM (Large Language Model).

Fluxo de dados:
  DynamoDB (Kp atual) ─┐
  LSTM predict.py      ├─→ bulletin_generator.py → OpenAI/Bedrock → Boletim
  YOLO inference.py    ┘         ↓
                              SNS → E-mail de alerta (se risco alto)
                              S3  → Arquivo do boletim

POR QUE LLM AQUI?
  Dados numéricos isolados (Kp=7.2, B=-2600 nT) são difíceis de
  interpretar por operadores não especialistas. O LLM traduz esses
  números em linguagem operacional: "Risco ALTO — satélites em órbita
  baixa podem sofrer arrasto aumentado. Operadores de rede elétrica
  devem ativar protocolo de proteção em transformadores de alta tensão."

ESTRATÉGIA DE FALLBACK:
  1. OpenAI gpt-4o-mini (primário) — requer OPENAI_API_KEY no .env
  2. Amazon Bedrock Claude (fallback) — usa LabRole, sem custo extra
  3. Template estático (fallback final) — funciona sem API externa

Uso:
    python src/cognitive/bulletin_generator.py
    python src/cognitive/bulletin_generator.py --storm
    python src/cognitive/bulletin_generator.py --output json
"""

import argparse
import json
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv()

SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:065818678123:helios-storm-alerts"
S3_BUCKET     = "helios-solar-data"
AWS_REGION    = "us-east-1"
DYNAMO_TABLE  = "helios-kp-realtime"

# Limiar de Kp para disparo de alerta SNS
KP_ALERT_THRESHOLD = 5.0

ROOT      = Path(__file__).parent.parent.parent
MODEL_DIR = ROOT / "src" / "ml" / "lstm" / "model"


# ─── 1. Coleta de dados dos sensores e modelos ────────────────────────────────

def get_latest_kp_readings(n: int = 6) -> list[dict]:
    """Busca as últimas n leituras de Kp/campo magnético do DynamoDB."""
    try:
        dynamo = boto3.resource("dynamodb", region_name=AWS_REGION)
        table  = dynamo.Table(DYNAMO_TABLE)
        resp   = table.scan(Limit=50)
        items  = sorted(resp.get("Items", []), key=lambda x: x.get("timestamp", ""), reverse=True)
        return items[:n]
    except Exception as e:
        print(f"  [DynamoDB] {e}")
        return []


def get_lstm_forecast() -> dict:
    """Executa a previsão LSTM e retorna o JSON de previsão."""
    try:
        import sys
        sys.path.insert(0, str(ROOT / "src" / "ml" / "lstm"))
        from predict import run_prediction
        return run_prediction(months=6)
    except Exception:
        # Fallback: retorna previsão simulada se modelo não disponível
        return {
            "forecast": [
                {"month": i + 1, "ssn": 85 + i * 5, "risk": "ACTIVE"}
                for i in range(6)
            ],
            "source": "fallback_simulated",
        }


def get_yolo_detection() -> dict:
    """Executa detecção YOLO na imagem SDO mais recente."""
    try:
        import sys
        sys.path.insert(0, str(ROOT / "src" / "ml" / "yolo"))
        from inference import run_inference, download_latest_sdo
        from pathlib import Path as P
        img_path = ROOT / "data" / "solar_images" / "sdo_latest_0193.jpg"
        download_latest_sdo(img_path)
        return run_inference(str(img_path), save_annotated=False)
    except Exception as e:
        return {
            "total_detected": 0,
            "detections": [],
            "risk_score": 0.0,
            "risk_level": "QUIET",
            "source": "fallback",
        }


# ─── 2. Construção do prompt ──────────────────────────────────────────────────

def build_prompt(kp_readings: list, lstm_forecast: dict, yolo_result: dict) -> str:
    """Constrói o prompt técnico para o LLM."""

    # Resumo das leituras magnéticas
    if kp_readings:
        b_values  = [float(r.get("b_total_nT", 23000)) for r in kp_readings]
        b_mean    = sum(b_values) / len(b_values)
        b_min     = min(b_values)
        geo_stati = [r.get("geo_status", "QUIET") for r in kp_readings]
        dominant  = max(set(geo_stati), key=geo_stati.count)
        kp_proxies = [float(r.get("kp_proxy", 0)) for r in kp_readings]
        kp_mean   = sum(kp_proxies) / len(kp_proxies)
    else:
        b_mean, b_min, dominant, kp_mean = 23000, 23000, "QUIET", 0

    # Resumo da previsão LSTM
    forecast_lines = []
    for f in lstm_forecast.get("forecast", [])[:3]:
        forecast_lines.append(f"  Mês +{f['month']}: SSN={f['ssn']:.0f}, Risco={f['risk']}")
    forecast_str = "\n".join(forecast_lines) if forecast_lines else "  Dados indisponíveis"

    # Resumo das detecções YOLO
    detections = yolo_result.get("detections", [])
    yolo_str = f"{yolo_result.get('total_detected', 0)} objetos detectados, " \
               f"risk_score={yolo_result.get('risk_score', 0):.2f}, " \
               f"nível={yolo_result.get('risk_level', 'QUIET')}"

    prompt = f"""Você é um sistema especialista em meteorologia espacial operando em tempo real.
Gere um boletim técnico CONCISO (máximo 300 palavras) em português para operadores de infraestrutura crítica.

═══════════════ DADOS DOS SENSORES ═══════════════

[Campo Magnético — Estação São Paulo (últimas leituras)]
  Campo médio:     {b_mean:.0f} nT  (referência quieto: ~23.000 nT)
  Campo mínimo:    {b_min:.0f} nT
  Status dominante: {dominant}
  Kp proxy médio:  {kp_mean:.1f}

[Previsão LSTM — Atividade Solar (próximos 3 meses)]
{forecast_str}

[Detecção YOLO — Imagem SDO mais recente]
  {yolo_str}

═══════════════ FORMATO DO BOLETIM ═══════════════

O boletim DEVE conter exatamente estas 4 seções:

## NÍVEL DE RISCO ATUAL
[BAIXO / MODERADO / ALTO / EXTREMO] — justificativa em 1 frase

## INFRAESTRUTURAS EM RISCO
Lista dos sistemas em risco com impacto esperado

## JANELA TEMPORAL DE MAIOR RISCO
Estimativa de quando o risco será máximo

## RECOMENDAÇÕES OPERACIONAIS
3-4 ações concretas para operadores

---
Data/Hora: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
Sistema: HeliOS v1.0 | FIAP Global Solution 2026
"""
    return prompt


# ─── 3. Geração do boletim via LLM ───────────────────────────────────────────

def generate_with_openai(prompt: str) -> str:
    """Tenta gerar via OpenAI gpt-4o-mini."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada no .env")

    import openai
    client = openai.OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.3,
    )
    return resp.choices[0].message.content


def generate_with_bedrock(prompt: str) -> str:
    """Fallback: Amazon Bedrock Claude Haiku (usa LabRole, sem custo extra)."""
    bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 600,
        "messages": [{"role": "user", "content": prompt}],
    })
    resp = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(resp["body"].read())
    return result["content"][0]["text"]


def generate_static_bulletin(kp_readings: list, yolo_result: dict) -> str:
    """Fallback final: boletim baseado em templates sem API externa."""
    risk_level = yolo_result.get("risk_level", "QUIET")
    geo_status = kp_readings[0].get("geo_status", "QUIET") if kp_readings else "QUIET"

    risk_map = {
        "QUIET":       ("BAIXO",    "Atividade solar dentro do normal."),
        "ACTIVE":      ("MODERADO", "Região ativa detectada no disco solar."),
        "WATCH":       ("MODERADO", "Múltiplas regiões ativas em monitoramento."),
        "WARNING":     ("ALTO",     "Perturbação geomagnética em progresso."),
        "STORM_MINOR": ("ALTO",     "Tempestade geomagnética G1-G2 em curso."),
        "STORM_MAJOR": ("EXTREMO",  "Tempestade geomagnética G3+ — protocolo de emergência."),
        "ALERT":       ("EXTREMO",  "Erupção solar de grande intensidade detectada."),
    }

    combined = "STORM_MAJOR" if "STORM" in geo_status else risk_level
    nivel, justificativa = risk_map.get(combined, ("BAIXO", "Condições normais."))

    return f"""## NÍVEL DE RISCO ATUAL
{nivel} — {justificativa}

## INFRAESTRUTURAS EM RISCO
- Satélites em LEO: aumento de arrasto atmosférico
- Redes elétricas: risco de correntes induzidas em transformadores
- GPS/GNSS: degradação de precisão em altas latitudes
- Comunicações HF: possível interrupção em rotas polares

## JANELA TEMPORAL DE MAIOR RISCO
Próximas 12-24 horas, com pico esperado entre 6-12h caso CME confirmada.

## RECOMENDAÇÕES OPERACIONAIS
1. Operadores de satélites: aumentar frequência de manobras corretivas de órbita
2. Redes elétricas: ativar monitoramento contínuo de transformadores de AT
3. Aviação polar: considerar rotas alternativas em latitudes < 60°N/S
4. GPS crítico: alternar para modo redundante com INS

---
Data/Hora: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
Sistema: HeliOS v1.0 | FIAP Global Solution 2026 | [BOLETIM AUTOMÁTICO - TEMPLATE]"""


def generate_bulletin(prompt: str, kp_readings: list, yolo_result: dict) -> tuple[str, str]:
    """
    Tenta gerar o boletim com fallback em cascata:
    OpenAI → Bedrock → Template estático

    Returns:
        (texto_do_boletim, fonte_usada)
    """
    # Tentativa 1: OpenAI
    try:
        text = generate_with_openai(prompt)
        return text, "openai/gpt-4o-mini"
    except Exception as e:
        print(f"  [OpenAI] {e} — tentando Bedrock...")

    # Tentativa 2: Bedrock
    try:
        text = generate_with_bedrock(prompt)
        return text, "aws/bedrock-claude-haiku"
    except Exception as e:
        print(f"  [Bedrock] {e} — usando template estático...")

    # Fallback final
    text = generate_static_bulletin(kp_readings, yolo_result)
    return text, "template_static"


# ─── 4. Envio de alerta SNS ───────────────────────────────────────────────────

def send_sns_alert(bulletin: str, risk_level: str, kp_proxy: float) -> bool:
    """Publica alerta no SNS se o risco justificar."""
    try:
        sns = boto3.client("sns", region_name=AWS_REGION)
        subject = f"⚡ HeliOS ALERTA — Tempestade Solar | Risco {risk_level} | Kp~{kp_proxy:.1f}"
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject[:100],
            Message=bulletin,
        )
        return True
    except Exception as e:
        print(f"  [SNS] {e}")
        return False


# ─── 5. Persistência no S3 ────────────────────────────────────────────────────

def save_to_s3(bulletin: str, metadata: dict) -> str | None:
    """Salva boletim em S3: bulletins/YYYY/MM/DD/HH-MM.json"""
    try:
        s3   = boto3.client("s3", region_name=AWS_REGION)
        now  = datetime.now(timezone.utc)
        key  = f"bulletins/{now.strftime('%Y/%m/%d/%H-%M')}.json"
        body = json.dumps({
            "bulletin": bulletin,
            "metadata": metadata,
            "generated_at": now.isoformat(),
        }, ensure_ascii=False, indent=2)
        s3.put_object(Bucket=S3_BUCKET, Key=key, Body=body, ContentType="application/json")
        return f"s3://{S3_BUCKET}/{key}"
    except Exception as e:
        print(f"  [S3] {e}")
        return None


# ─── Main ─────────────────────────────────────────────────────────────────────

def run(output_format: str = "pretty", storm_mode: bool = False) -> dict:
    print("=" * 60)
    print("  HeliOS — Gerador de Boletim Cognitivo")
    print("=" * 60)

    # 1. Coletar dados
    print("\n[1/5] Coletando leituras do DynamoDB...")
    kp_readings = get_latest_kp_readings(6)
    if storm_mode:
        # Sobrescreve com dados de tempestade para demonstração do alerta SNS
        kp_readings = [{"b_total_nT": "20400", "kp_proxy": "5.8",
                        "geo_status": "STORM_MAJOR", "timestamp": datetime.now(timezone.utc).isoformat()}
                       for _ in range(3)]
    print(f"  {len(kp_readings)} leituras encontradas")

    print("\n[2/5] Executando previsão LSTM...")
    lstm_forecast = get_lstm_forecast()
    print(f"  Fonte: {lstm_forecast.get('source', 'model')}")

    print("\n[3/5] Executando detecção YOLO na imagem SDO...")
    yolo_result = get_yolo_detection()
    print(f"  {yolo_result.get('total_detected', 0)} objetos | risk_level={yolo_result.get('risk_level', 'QUIET')}")

    # 2. Gerar boletim
    print("\n[4/5] Gerando boletim via LLM...")
    prompt  = build_prompt(kp_readings, lstm_forecast, yolo_result)
    bulletin, source = generate_bulletin(prompt, kp_readings, yolo_result)
    print(f"  Fonte: {source}")

    # 3. Determinar se alerta é necessário
    kp_proxies = [float(r.get("kp_proxy", 0)) for r in kp_readings]
    kp_max = max(kp_proxies) if kp_proxies else 0
    risk_level = yolo_result.get("risk_level", "QUIET")
    should_alert = kp_max >= KP_ALERT_THRESHOLD or risk_level in ("WARNING", "ALERT")

    print(f"\n[5/5] Publicando resultados...")
    # SNS
    sns_sent = False
    if should_alert:
        sns_sent = send_sns_alert(bulletin, risk_level, kp_max)
        print(f"  SNS alerta : {'✅ enviado' if sns_sent else '❌ erro'}")
    else:
        print(f"  SNS alerta : ⏭ não necessário (Kp_max={kp_max:.1f} < {KP_ALERT_THRESHOLD})")

    # S3
    metadata = {"source": source, "kp_max": kp_max, "risk_level": risk_level,
                 "should_alert": should_alert}
    s3_path = save_to_s3(bulletin, metadata)
    print(f"  S3         : {'✅ ' + s3_path if s3_path else '❌ erro'}")

    result = {
        "bulletin": bulletin,
        "source": source,
        "risk_level": risk_level,
        "kp_max": kp_max,
        "sns_sent": sns_sent,
        "s3_path": s3_path,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if output_format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 60)
        print(bulletin)
        print("=" * 60)

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HeliOS — Boletim Cognitivo")
    parser.add_argument("--output", choices=["pretty", "json"], default="pretty")
    parser.add_argument("--storm",  action="store_true", help="Força dados de tempestade para teste")
    args = parser.parse_args()
    run(output_format=args.output, storm_mode=args.storm)
