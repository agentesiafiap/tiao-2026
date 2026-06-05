#!/bin/bash
# iot_setup.sh — Setup completo do AWS IoT Core para HeliOS
# HeliOS | Global Solution 2026.1 — FIAP
#
# ATENÇÃO: Este script requer permissões iot:* que NÃO estão disponíveis
# no ambiente Vocareum/Lab. Documente aqui os comandos que seriam executados
# em uma conta AWS real (ex: conta pessoal após o curso).
#
# Para demonstração na disciplina, o simulador Python (simulate_esp32.py)
# publica via MQTT público (HiveMQ) e escreve diretamente no DynamoDB.
#
# Uso (conta AWS real):
#   chmod +x src/iot/iot_setup.sh
#   ./src/iot/iot_setup.sh
#
# Pré-requisitos:
#   - AWS CLI configurado com permissões iot:* e iam:AttachThingPrincipal
#   - jq instalado: brew install jq

set -euo pipefail

REGION="us-east-1"
THING_NAME="helios-magnetometer-station"
POLICY_NAME="helios-iot-policy"
CERTS_DIR="src/iot/certs"

mkdir -p "$CERTS_DIR"

echo "=========================================="
echo " HeliOS — Setup AWS IoT Core"
echo "=========================================="

# ─── 1. Criar Thing ───────────────────────────────────────────────────────────
echo ""
echo "[1/5] Criando Thing: $THING_NAME"
aws iot create-thing \
    --thing-name "$THING_NAME" \
    --region "$REGION" \
    --output json | jq '.thingArn'

# ─── 2. Criar certificado e chave privada ─────────────────────────────────────
echo ""
echo "[2/5] Gerando certificado mTLS..."
CERT_OUTPUT=$(aws iot create-keys-and-certificate \
    --set-as-active \
    --region "$REGION" \
    --output json)

CERT_ID=$(echo "$CERT_OUTPUT"   | jq -r '.certificateId')
CERT_ARN=$(echo "$CERT_OUTPUT"  | jq -r '.certificateArn')

echo "$CERT_OUTPUT" | jq -r '.certificatePem'          > "$CERTS_DIR/certificate.pem.crt"
echo "$CERT_OUTPUT" | jq -r '.keyPair.PrivateKey'       > "$CERTS_DIR/private.pem.key"
echo "$CERT_OUTPUT" | jq -r '.keyPair.PublicKey'        > "$CERTS_DIR/public.pem.key"

echo "  Certificate ID : $CERT_ID"
echo "  Salvo em       : $CERTS_DIR/"

# ─── 3. Baixar Amazon Root CA ─────────────────────────────────────────────────
echo ""
echo "[3/5] Baixando Amazon Root CA 1..."
curl -s https://www.amazontrust.com/repository/AmazonRootCA1.pem \
    -o "$CERTS_DIR/AmazonRootCA1.pem"
echo "  Salvo em: $CERTS_DIR/AmazonRootCA1.pem"

# ─── 4. Criar e anexar policy IoT ─────────────────────────────────────────────
echo ""
echo "[4/5] Criando policy IoT: $POLICY_NAME"

ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)

POLICY_DOC=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect",
        "iot:Publish",
        "iot:Subscribe",
        "iot:Receive"
      ],
      "Resource": [
        "arn:aws:iot:$REGION:$ACCOUNT_ID:client/$THING_NAME",
        "arn:aws:iot:$REGION:$ACCOUNT_ID:topic/helios/magnetometer",
        "arn:aws:iot:$REGION:$ACCOUNT_ID:topicfilter/helios/*"
      ]
    }
  ]
}
EOF
)

aws iot create-policy \
    --policy-name "$POLICY_NAME" \
    --policy-document "$POLICY_DOC" \
    --region "$REGION" \
    --output json | jq '.policyArn'

aws iot attach-policy \
    --policy-name "$POLICY_NAME" \
    --target "$CERT_ARN" \
    --region "$REGION"

aws iot attach-thing-principal \
    --thing-name "$THING_NAME" \
    --principal "$CERT_ARN" \
    --region "$REGION"

echo "  Policy criada e anexada ao certificado."

# ─── 5. Criar IoT Rule → DynamoDB ────────────────────────────────────────────
echo ""
echo "[5/5] Criando IoT Rule: helios-mqtt-to-dynamodb"

RULE_SQL="SELECT *, timestamp() as timestamp FROM 'helios/magnetometer'"

aws iot create-topic-rule \
    --rule-name "heliosMqttToDynamoDB" \
    --topic-rule-payload "{
      \"sql\": \"$RULE_SQL\",
      \"actions\": [{
        \"dynamoDBv2\": {
          \"roleArn\": \"arn:aws:iam::$ACCOUNT_ID:role/LabRole\",
          \"putItem\": {
            \"tableName\": \"helios-kp-realtime\"
          }
        }
      }],
      \"ruleDisabled\": false
    }" \
    --region "$REGION"

echo "  IoT Rule criada: helios/magnetometer → DynamoDB helios-kp-realtime"

# ─── Resumo ───────────────────────────────────────────────────────────────────
IOT_ENDPOINT=$(aws iot describe-endpoint \
    --endpoint-type iot:Data-ATS \
    --region "$REGION" \
    --query 'endpointAddress' \
    --output text)

echo ""
echo "=========================================="
echo " Setup concluído!"
echo "=========================================="
echo " Endpoint IoT : $IOT_ENDPOINT"
echo " Certificados : $CERTS_DIR/"
echo ""
echo " Próximo passo: cole o endpoint e os certs no esp32_magnetometer.ino"
echo " Ou use: python src/iot/simulate_esp32.py (sem certificados necessários)"
