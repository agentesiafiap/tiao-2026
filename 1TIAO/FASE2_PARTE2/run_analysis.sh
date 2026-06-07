#!/bin/bash
# Script de Orquestração da Análise de Dados (Bash)

# Variáveis de Caminho
PYTHON_API="scripts/python_api/api_weather.py"
PYTHON_CAPTURA="scripts/r_analysis/log_capturer.py"
PYTHON_LIMPEZA="scripts/r_analysis/data_cleaner.py"
R_ANALYSIS="scripts/r_analysis/data_analysis.R"
REQUIREMENTS_FILE="scripts/config/requirements.txt"

# Variável para o número de linhas a capturar
NUM_LINHAS=30

echo "=========================================================="
echo "         PIPELINE DE DATA SCIENCE (Fase 2)                "
echo "=========================================================="

# Função para executar comandos PlatformIO com segurança (pressupõe que 'pio' está no PATH)
function pio_cmd {
    pio "$@"
    if [ $? -ne 0 ]; then
        echo "ERRO: Falha ao executar 'pio $@'. Verifique a instalação do PlatformIO."
        exit 1
    fi
}

# ------------------------------------------------------------
# PASSO 0.0: INSTALAR DEPENDÊNCIAS PYTHON
# ------------------------------------------------------------
echo "--- PASSO 0.0: INSTALANDO DEPENDÊNCIAS PYTHON ---"
if [ -f "$REQUIREMENTS_FILE" ]; then
    python3 -m pip install -r "$REQUIREMENTS_FILE" --break-system-packages
    if [ $? -ne 0 ]; then
        echo "ERRO: Falha na instalação das dependências Python. Verifique sua conexão ou ambiente."
        exit 1
    fi
    echo "Dependências Python instaladas/verificadas com sucesso."
else
    echo "AVISO: Arquivo '$REQUIREMENTS_FILE' não encontrado. As dependências Python podem não estar instaladas."
fi

# ------------------------------------------------------------
# PASSO 0.1: COMPILAÇÃO DO FIRMWARE
# ------------------------------------------------------------
echo "--- PASSO 0.1: COMPILANDO PROJETO ESP32 ---"
pio_cmd run

# ------------------------------------------------------------
# PASSO 0.2: INÍCIO MANUAL DA SIMULAÇÃO (PONTO CRÍTICO)
# ------------------------------------------------------------
echo "=========================================================="
echo " ACAO REQUERIDA: INICIE A SIMULACAO WOKWI NO VS CODE AGORA."
echo "=========================================================="
echo "Aguardando 10 segundos..."
sleep 10
read -p ">> Pressione [ENTER] APÓS a simulação Wokwi ter sido iniciada e o firmware carregado. "

echo "Aguardando 15 segundos adicionais para a porta serial (4000) abrir completamente..."
sleep 15


# ------------------------------------------------------------
# PASSO 1: DECISÃO DA API DO TEMPO (Opcional 1)
# ------------------------------------------------------------
echo ""
echo "--- PASSO 1: DECISÃO DA API (Open-Meteo) ---"
API_STATUS=$(python3 "$PYTHON_API" | tail -n 1 | grep -o '[01]$')

if [ -z "$API_STATUS" ]; then
    echo "AVISO: Falha ao obter status da API. Usando 0 (OK) por padrão."
    API_STATUS=0
fi
echo "Status de Bloqueio da API obtido: $API_STATUS"

# ------------------------------------------------------------
# PASSO 2: ENVIO DO BLOQUEIO EXTERNO PARA O ESP32
# ------------------------------------------------------------
echo "--- PASSO 2: ENVIANDO STATUS DE BLOQUEIO ($API_STATUS) ---"
# O timeout de 5s no Python é essencial aqui para não travar o script se a porta ainda estiver fechada.
python3 -c "import serial; ser = serial.serial_for_url('rfc2217://localhost:4000', baudrate=115200, timeout=5); ser.write(b'$API_STATUS'); print(f'Enviado $API_STATUS via serial.'); ser.close()"

if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao enviar dado para a porta 4000. A simulação Wokwi não está ativa ou a porta não abriu."
    exit 1
fi

# ------------------------------------------------------------
# PASSO 3: CAPTURA DE DADOS DO ESP32
# ------------------------------------------------------------
echo ""
echo "--- PASSO 3: CAPTURANDO $NUM_LINHAS LINHAS DE LOG ---"
python3 "$PYTHON_CAPTURA" $NUM_LINHAS

if [ $? -ne 0 ]; then
    echo "ERRO: Falha na captura do log serial. Abortando."
    exit 1
fi

# ------------------------------------------------------------
# PASSO 4: LIMPEZA E FORMATAÇÃO DE DADOS
# ------------------------------------------------------------
echo ""
echo "--- PASSO 4: PREPARANDO CSV PARA ANÁLISE EM R ---"
python3 "$PYTHON_LIMPEZA"

if [ $? -ne 0 ]; then
    echo "ERRO: Falha na limpeza. Abortando."
    exit 1
fi

# ------------------------------------------------------------
# PASSO 5: EXECUÇÃO DA ANÁLISE R (Opcional 2)
# ------------------------------------------------------------
echo ""
echo "--- PASSO 5: EXECUTANDO ANÁLISE ESTATÍSTICA (R) ---"
Rscript "$R_ANALYSIS"

echo ""
echo "=========================================================="
echo "PIPELINE CONCLUÍDO."
echo "=========================================================="