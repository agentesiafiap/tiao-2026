# HeliOS — Plano de Implementação por Fases
## Sistema de Predição de Tempestades Solares e Impacto em Infraestrutura Crítica
### Global Solution 2026.1 — FIAP | 2º Ano TIAO

---

## Visão Geral do Projeto

**Pergunta central respondida:** Como a IA pode usar dados espaciais reais para proteger infraestruturas críticas na Terra de tempestades solares?

**Stack tecnológica completa:**

| Conceito do Curso | Implementação no HeliOS |
|---|---|
| Redes neurais | LSTM para previsão de índice Kp |
| YOLO | Detecção e classificação de manchas solares em imagens SDO |
| Pipelines de dados | S3 → Lambda → DynamoDB/RDS |
| AWS | S3, Lambda, API Gateway, IoT Core, SNS, EventBridge |
| Computação serverless | Lambda para ingestão, transformação e inferência |
| ESP32 | Simulação de magnetômetro terrestre via MQTT |
| APIs cognitivas | OpenAI API para boletins em linguagem natural |
| SQL | RDS PostgreSQL para histórico de eventos |
| NoSQL | DynamoDB para leituras de sensores em tempo real |
| Análise de dados em tempo real | Kinesis / streaming de leituras do ESP32 |

---

## Pré-requisitos (verificar antes de iniciar)

- [ ] Python 3.10+ instalado (`python --version`)
- [ ] AWS CLI instalado e configurado com conta free tier (`aws configure`)
- [ ] Git instalado e conta GitHub disponível
- [ ] Conta OpenAI com crédito mínimo (ou usar Amazon Bedrock como alternativa)
- [ ] Arduino IDE instalado (para compilar código ESP32)
- [ ] ESP32 físico disponível **OU** aceitar simulação via script Python

**Verificação rápida do ambiente:**
```bash
python3 --version
aws sts get-caller-identity
git --version
```

---

## Estrutura do Repositório (baseada no template FIAP)

```
helios-gs2/
├── README.md                        # Template FIAP preenchido
├── data/
│   ├── raw/                         # Dados brutos das APIs NASA/NOAA
│   ├── processed/                   # Dados tratados para treino do LSTM
│   └── solar_images/                # Imagens SDO para YOLO
├── src/
│   ├── ingestion/                   # Scripts de coleta de dados (Fase 2)
│   ├── pipeline/                    # Lambdas e pipeline AWS (Fase 3)
│   ├── database/                    # Setup SQL/NoSQL (Fase 4)
│   ├── ml/
│   │   ├── lstm/                    # Modelo de previsão Kp (Fase 5)
│   │   └── yolo/                    # Detecção de manchas solares (Fase 6)
│   ├── iot/                         # Código ESP32 + MQTT (Fase 7)
│   ├── cognitive/                   # API cognitiva + SNS (Fase 8)
│   └── dashboard/                   # Streamlit (Fase 9)
└── docs/
    ├── arquitetura.png              # Diagrama da solução
    ├── fluxograma.png               # Fluxo de dados
    └── decisoes_tecnicas.md         # Registro de decisões
```

---

## FASE 1 — Setup do Projeto e Repositório

**Objetivo:** Repositório GitHub criado com estrutura do template FIAP, README raiz preenchido e ambiente local configurado.

**Entregável verificável:** `git clone` funciona e estrutura de pastas está correta.

### Instruções para o agente:
1. Criar repositório GitHub `helios-gs2` (público)
2. Clonar e replicar estrutura de pastas acima
3. Criar `README.md` raiz seguindo template FIAP com:
   - Nome do projeto: **HeliOS**
   - Nomes dos integrantes (preencher)
   - Descrição do projeto (~300 palavras)
   - Seção "Como executar" com lista de pré-requisitos
4. Criar `requirements.txt` inicial com dependências base:
   ```
   boto3>=1.34
   requests>=2.31
   python-dotenv>=1.0
   pandas>=2.0
   numpy>=1.26
   ```
5. Criar `.env.example` com variáveis necessárias:
   ```
   AWS_REGION=us-east-1
   OPENAI_API_KEY=
   NASA_API_KEY=DEMO_KEY
   S3_BUCKET_NAME=helios-solar-data
   ```
6. Criar `.gitignore` (Python + AWS + `.env`)
7. Commit inicial e push

**Checklist de conclusão:**
- [ ] Repositório público no GitHub
- [ ] Estrutura de pastas criada
- [ ] README com nomes dos integrantes
- [ ] `.env.example` sem credenciais reais
- [ ] Primeiro commit feito

---

## FASE 2 — Ingestão de Dados Reais (NASA + NOAA)

**Objetivo:** Scripts Python que consomem as APIs reais da NASA e NOAA e salvam dados em S3.

**Entregável verificável:** Executar os scripts localmente e ver arquivos JSON/CSV aparecendo no bucket S3.

**APIs utilizadas (gratuitas, sem autenticação complexa):**
- `https://api.nasa.gov/DONKI/` — eventos solares (chave: `DEMO_KEY` para testes)
- `https://services.swpc.noaa.gov/json/planetary_k_index_1m.json` — índice Kp em tempo real
- `https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json` — histórico solar

### Instruções para o agente:
1. Criar `src/ingestion/nasa_donki.py`:
   - Consome eventos: CME, Solar Flare, Geomagnetic Storm, SEP
   - Parâmetros: data início/fim configuráveis via `.env`
   - Salva JSON em `data/raw/donki/` localmente
   - Faz upload para `s3://helios-solar-data/raw/donki/YYYY-MM-DD.json`
2. Criar `src/ingestion/noaa_kp.py`:
   - Consome índice Kp em tempo real (atualizado a cada minuto pela NOAA)
   - Salva em `data/raw/kp/kp_realtime.json`
   - Upload para S3 em `raw/kp/`
3. Criar `src/ingestion/noaa_historical.py`:
   - Baixa série histórica completa de índice Kp (desde 1932)
   - Salva como CSV em `data/processed/kp_historical.csv`
4. Criar `src/ingestion/solar_images.py`:
   - Baixa imagens do SDO (Solar Dynamics Observatory) via `https://sdo.gsfc.nasa.gov/assets/img/latest/`
   - Salva JPEGs em `data/solar_images/`
5. Criar `src/ingestion/run_all.py` que executa todos os scripts em sequência
6. Criar bucket S3:
   ```bash
   aws s3 mb s3://helios-solar-data --region us-east-1
   ```

**Checklist de conclusão:**
- [ ] `python src/ingestion/run_all.py` executa sem erros
- [ ] Arquivos visíveis em `data/raw/`
- [ ] `aws s3 ls s3://helios-solar-data/raw/` retorna arquivos
- [ ] Pelo menos 1 imagem solar baixada em `data/solar_images/`

---

## FASE 3 — Pipeline Serverless AWS

**Objetivo:** Lambda automatizada que executa a ingestão a cada hora e roteia dados para os destinos corretos.

**Entregável verificável:** Trigger manual da Lambda via CLI retorna sucesso e novos dados aparecem no S3.

**Arquitetura:**
```
EventBridge (cron hourly)
    → Lambda: helios-ingestion
        → NASA DONKI API → S3 raw/donki/
        → NOAA Kp API   → S3 raw/kp/
    → Lambda: helios-transform
        → S3 raw/ → transformação → S3 processed/
        → DynamoDB (dados em tempo real)
        → RDS PostgreSQL (histórico)
```

### Instruções para o agente:
1. Criar IAM role `helios-lambda-role` com políticas:
   - `AWSLambdaBasicExecutionRole`
   - Acesso ao S3 bucket `helios-solar-data`
   - Acesso ao DynamoDB
   - Acesso ao RDS
   ```bash
   # Agente gerará os comandos aws iam exatos
   ```
2. Criar `src/pipeline/lambda_ingestion.py` — versão da Fase 2 adaptada para Lambda handler
3. Criar `src/pipeline/lambda_transform.py` — lê S3 raw, limpa e normaliza dados
4. Empacotar e fazer deploy das Lambdas:
   ```bash
   cd src/pipeline
   zip -r lambda_ingestion.zip lambda_ingestion.py
   aws lambda create-function --function-name helios-ingestion \
     --runtime python3.12 --handler lambda_ingestion.lambda_handler \
     --role arn:aws:iam::ACCOUNT_ID:role/helios-lambda-role \
     --zip-file fileb://lambda_ingestion.zip
   ```
5. Criar EventBridge rule para trigger horário:
   ```bash
   aws events put-rule --schedule-expression "rate(1 hour)" \
     --name helios-hourly-trigger --state ENABLED
   ```
6. Testar trigger manual:
   ```bash
   aws lambda invoke --function-name helios-ingestion output.json
   cat output.json
   ```

**Checklist de conclusão:**
- [ ] Lambda `helios-ingestion` deployada e invocável
- [ ] Lambda `helios-transform` deployada
- [ ] EventBridge rule criada
- [ ] Invocação manual retorna `{"statusCode": 200}`
- [ ] Dados em `s3://helios-solar-data/processed/`

---

## FASE 4 — Bancos de Dados (SQL + NoSQL)

**Objetivo:** DynamoDB para dados em tempo real e RDS PostgreSQL para histórico de eventos, ambos alimentados pelo pipeline.

**Entregável verificável:** Query no DynamoDB retorna leituras Kp recentes; query SQL no RDS retorna histórico de eventos.

### Instruções para o agente:
1. Criar tabela DynamoDB `helios-kp-realtime`:
   ```bash
   aws dynamodb create-table \
     --table-name helios-kp-realtime \
     --attribute-definitions AttributeName=timestamp,AttributeType=S \
     --key-schema AttributeName=timestamp,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST
   ```
2. Criar tabela DynamoDB `helios-solar-events`:
   - Partition key: `event_id` (String)
   - Sort key: `event_type` (String)
3. Criar instância RDS PostgreSQL (free tier: `db.t3.micro`):
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier helios-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username helios \
     --master-user-password [SENHA_SEGURA] \
     --allocated-storage 20 \
     --publicly-accessible
   ```
4. Criar `src/database/schema.sql` com DDL:
   ```sql
   CREATE TABLE kp_history (
       id SERIAL PRIMARY KEY,
       observed_time TIMESTAMPTZ NOT NULL,
       kp_index DECIMAL(4,2),
       source VARCHAR(20),
       created_at TIMESTAMPTZ DEFAULT NOW()
   );

   CREATE TABLE solar_events (
       id SERIAL PRIMARY KEY,
       event_id VARCHAR(100) UNIQUE,
       event_type VARCHAR(50),
       start_time TIMESTAMPTZ,
       peak_time TIMESTAMPTZ,
       end_time TIMESTAMPTZ,
       intensity VARCHAR(20),
       location VARCHAR(50),
       raw_data JSONB,
       created_at TIMESTAMPTZ DEFAULT NOW()
   );

   CREATE INDEX idx_kp_history_time ON kp_history(observed_time);
   CREATE INDEX idx_solar_events_type ON solar_events(event_type, start_time);
   ```
5. Criar `src/database/seed.py` que carrega `data/processed/kp_historical.csv` no RDS
6. Atualizar Lambda `helios-transform` para gravar em ambos os bancos
7. Verificação:
   ```bash
   aws dynamodb scan --table-name helios-kp-realtime --max-items 5
   psql -h [RDS_ENDPOINT] -U helios -d postgres -c "SELECT COUNT(*) FROM kp_history;"
   ```

**Checklist de conclusão:**
- [ ] DynamoDB com dados em tempo real
- [ ] RDS com schema criado
- [ ] `seed.py` carregou dados históricos no PostgreSQL
- [ ] Query de verificação retorna dados em ambos os bancos

> ⚠ **Gestão de custo:** Após concluir e validar o RDS, executar imediatamente:
> ```bash
> aws rds stop-db-instance --db-instance-identifier helios-db
> ```
> Religar apenas para as fases que exigirem acesso ao PostgreSQL (Fase 5 seed, Fase 9 dashboard histórico) e para a apresentação final.

---

## FASE 5 — Modelo LSTM (Previsão de Atividade Solar)

**Objetivo:** Rede neural LSTM treinada para prever o Sunspot Number (SSN) para os próximos 6 meses com base na série histórica NOAA (1749–2026), com classificação de risco geomagnético.

**Entregável verificável:** `predict.py` retorna JSON com previsão mensal de SSN + nível de risco (QUIET/ACTIVE/ELEVATED/STORM).

**Dataset:** `data/processed/solar_cycle_historical.csv` — 3329 registros mensais (NOAA Solar Cycle Indices).

> ### ⚠️ IMPEDIMENTO ENCONTRADO — TensorFlow/macOS ARM (2026-06-05)
>
> **Problema:** TensorFlow 2.21+ com Python 3.13 no macOS Apple Silicon (ARM) congela indefinidamente na Época 1 do treinamento. A causa é o compilador XLA/JIT tentando otimizar o grafo computacional para aceleradores (CUDA/Metal) que não estão configurados corretamente nesta combinação de versões.
>
> **Tentativas de mitigação:**
> - `os.environ["TF_XLA_FLAGS"] = "--tf_xla_auto_jit=0"` — não resolveu
> - `tf.config.optimizer.set_jit(False)` — não resolveu
> - `jit_compile=False` no `model.compile()` — não resolveu
> - Redução do dataset (600 amostras) e batch maior — não resolveu
>
> **Solução adotada: Treinamento no Google Colab (GPU T4)**
> - Script de treinamento portátil criado em `src/ml/lstm/colab_train.py`
> - Treinamento concluído em ~5 minutos com GPU T4 gratuita
> - Arquivos gerados baixados manualmente e colocados em `src/ml/lstm/model/`
> - Notebook de documentação: `src/ml/lstm/helios_lstm_colab.ipynb`

### Artefatos gerados:
- `src/ml/lstm/train.py` — script local (funcional para ambientes sem o bug)
- `src/ml/lstm/colab_train.py` — script portátil para Google Colab
- `src/ml/lstm/evaluate.py` — avaliação com MAE, RMSE e gráficos
- `src/ml/lstm/predict.py` — inferência com classificação de risco
- `src/ml/lstm/model/helios_lstm.keras` — modelo treinado ✅
- `src/ml/lstm/model/scaler.pkl` — MinMaxScaler serializado ✅
- `src/ml/lstm/model/model_meta.json` — metadados (MAE, RMSE, épocas) ✅
- `docs/lstm_training_metrics.png` — curvas de loss/MAE ✅

### Próximos passos pendentes:
4. Fazer upload do modelo para S3: `s3://helios-solar-data/models/lstm/`
5. Commit e push

**Checklist de conclusão:**
- [x] Scripts `train.py`, `evaluate.py`, `predict.py` criados
- [x] Modelo treinado (via Google Colab) e artefatos em `src/ml/lstm/model/`
- [x] Gráfico de métricas em `docs/lstm_training_metrics.png`
- [ ] Upload modelo para S3
- [ ] Commit e push da Fase 5

---

## FASE 6 — YOLO: Detecção de Manchas Solares

**Objetivo:** Modelo YOLO fine-tunado que detecta e classifica manchas solares em imagens do SDO, indicando correlação com atividade geomagnética.

**Entregável verificável:** Passar uma imagem solar pelo modelo e receber bounding boxes com classificação de intensidade.

**Dataset:** Imagens do Solar Dynamics Observatory (SDO) da NASA — gratuitas e públicas.

### Instruções para o agente:
1. Baixar dataset anotado:
   - Opção A: Dataset do [SolarNet](https://github.com/observethesun/SolarNet) (~2000 imagens anotadas)
   - Opção B: Usar `src/ingestion/solar_images.py` (Fase 2) + anotar ~100 imagens com [Label Studio](https://labelstud.io/) (open source)
   - **Usar Opção A** para velocidade — salvar em `data/solar_images/`
2. Instalar Ultralytics:
   ```bash
   pip install ultralytics
   ```
3. Criar `src/ml/yolo/dataset.yaml`:
   ```yaml
   path: data/solar_images
   train: images/train
   val: images/val
   nc: 3
   names: ['quiet_sun', 'active_region', 'sunspot_group']
   ```
4. Criar `src/ml/yolo/train.py`:
   ```python
   from ultralytics import YOLO
   model = YOLO('yolo11n.pt')  # nano — rápido para POC
   model.train(data='dataset.yaml', epochs=30, imgsz=640, batch=16)
   model.save('src/ml/yolo/model/helios_yolo.pt')
   ```
5. Criar `src/ml/yolo/inference.py`:
   - Baixa imagem SDO mais recente
   - Executa detecção
   - Retorna JSON: `{detections: [{class, confidence, bbox}], risk_score: float}`
   - Salva imagem anotada em `data/solar_images/annotated/`
6. Integrar inferência YOLO com pipeline:
   - Lambda `helios-solar-vision` executa inference a cada hora
   - Resultado gravado no DynamoDB `helios-solar-events`

**Checklist de conclusão:**
- [ ] Modelo fine-tunado com mAP50 > 0.5 no dataset de validação
- [ ] `inference.py` processa imagem e retorna JSON com detecções
- [ ] Imagem anotada com bounding boxes salva
- [ ] Lambda de visão integrada ao pipeline

---

## FASE 7 — ESP32: Simulação de Magnetômetro via MQTT

**Objetivo:** ESP32 (físico ou simulado) publica leituras de campo magnético via MQTT para AWS IoT Core, representando uma estação terrestre de monitoramento.

**Entregável verificável:** Dados do ESP32 aparecem no DynamoDB `helios-kp-realtime` em tempo real.

### Instruções para o agente:

**Se tiver ESP32 físico:**
1. Criar `src/iot/esp32_magnetometer.ino` (Arduino C++):
   ```cpp
   #include <WiFi.h>
   #include <PubSubClient.h>
   #include <ArduinoJson.h>

   // Gera leitura sintética de campo magnético (sem sensor físico necessário)
   // Simula variações típicas durante tempestade geomagnética
   float generateMagneticReading() {
     float baseline = 50000.0; // nanoTeslas — campo típico em São Paulo
     float variation = random(-500, 500) / 10.0;
     return baseline + variation;
   }

   void publishReading() {
     StaticJsonDocument<200> doc;
     doc["device_id"] = "helios-station-BR-001";
     doc["latitude"] = -23.5505;
     doc["longitude"] = -46.6333;
     doc["magnetic_field_nT"] = generateMagneticReading();
     doc["timestamp"] = millis();
     // publish to AWS IoT Core topic: helios/magnetometer
   }
   ```
2. Configurar AWS IoT Core: criar Thing, certificados, policy
3. Fazer upload dos certificados para o ESP32

**Se NÃO tiver ESP32 físico (simulação Python):**
1. Criar `src/iot/simulate_esp32.py`:
   - Usa `paho-mqtt` para publicar no AWS IoT Core
   - Gera leituras sintéticas plausíveis com variação senoidal + ruído
   - Loop de publicação a cada 30 segundos
2. Criar `src/iot/iot_setup.sh` com comandos de setup do IoT Core:
   ```bash
   aws iot create-thing --thing-name helios-magnetometer-station
   aws iot create-keys-and-certificate --set-as-active
   # ... demais comandos gerados pelo agente
   ```
3. Criar rule IoT Core que roteia mensagens MQTT para DynamoDB
4. Testar:
   ```bash
   python src/iot/simulate_esp32.py &
   aws dynamodb scan --table-name helios-kp-realtime --max-items 3
   ```

**Checklist de conclusão:**
- [ ] Código ESP32/simulador publica mensagens MQTT
- [ ] AWS IoT Core recebe mensagens (visível no console ou CLI)
- [ ] Dados chegam ao DynamoDB automaticamente via IoT Rule
- [ ] Código C++ do ESP32 incluído no repositório independentemente de ter hardware

---

## FASE 8 — API Cognitiva: Boletins Automáticos + Alertas SNS

**Objetivo:** Lambda que combina previsão LSTM + detecções YOLO + dados do ESP32 e gera boletim técnico em linguagem natural, enviando alertas via SNS quando risco for alto.

**Entregável verificável:** Invocar Lambda retorna boletim gerado por LLM e e-mail de alerta é recebido.

### Instruções para o agente:
1. Criar `src/cognitive/bulletin_generator.py`:
   ```python
   import openai

   def generate_bulletin(kp_forecast, solar_detections, magnetic_readings):
       prompt = f"""
       Você é um sistema especialista em meteorologia espacial.
       Com base nos seguintes dados, gere um boletim técnico em português:

       Previsão Kp próximas 24h: {kp_forecast}
       Detecções solares (YOLO): {solar_detections}
       Leituras magnéticas (ESP32): {magnetic_readings}

       O boletim deve incluir:
       1. Nível de risco atual (Baixo/Moderado/Alto/Extremo)
       2. Infraestruturas em risco (satélites, redes elétricas, GPS)
       3. Janela temporal de maior risco
       4. Recomendações operacionais
       """
       response = openai.chat.completions.create(
           model="gpt-4o-mini",
           messages=[{"role": "user", "content": prompt}]
       )
       return response.choices[0].message.content
   ```
2. Criar tópico SNS e subscription por e-mail:
   ```bash
   aws sns create-topic --name helios-storm-alerts
   aws sns subscribe --topic-arn arn:aws:sns:us-east-1:ACCOUNT:helios-storm-alerts \
     --protocol email --notification-endpoint SEU@EMAIL.COM
   ```
3. Criar Lambda `helios-cognitive`:
   - Coleta dados das últimas 6h do DynamoDB
   - Chama API de previsão (Fase 5)
   - Gera boletim via OpenAI
   - Se `kp_max_forecast >= 5`: publica alerta no SNS
   - Salva boletim no S3: `s3://helios-solar-data/bulletins/`
4. Adicionar trigger: EventBridge a cada 6 horas
5. Testar:
   ```bash
   aws lambda invoke --function-name helios-cognitive output.json
   cat output.json
   # verificar e-mail de alerta
   ```

**Checklist de conclusão:**
- [ ] Lambda gera boletim em português com dados reais
- [ ] SNS envia e-mail quando Kp previsto >= 5
- [ ] Boletins salvos no S3 com timestamp
- [ ] Custo OpenAI por chamada < $0.01 (usar gpt-4o-mini)

---

## FASE 9 — Dashboard Streamlit + Integração Final

**Objetivo:** Dashboard interativo que consolida todos os módulos: previsão LSTM, detecções YOLO, dados ESP32 em tempo real, boletins cognitivos e mapa de risco.

**Entregável verificável:** `streamlit run app.py` abre dashboard com dados reais, gráficos e mapa de risco.

### Instruções para o agente:
1. Instalar dependências do dashboard:
   ```bash
   pip install streamlit plotly folium streamlit-folium Pillow
   ```
2. Criar `src/dashboard/app.py` com seções:
   - **Cabeçalho:** Logo HeliOS + timestamp atualização
   - **Painel de risco atual:** metric cards (Kp atual, classificação, nível de alerta)
   - **Previsão 24h (LSTM):** gráfico de linha com banda de confiança
   - **Última imagem solar (YOLO):** imagem SDO anotada + tabela de detecções
   - **Leituras ESP32 em tempo real:** gráfico de série temporal das últimas 2h
   - **Mapa de impacto:** mapa mundial com regiões de maior exposição auroral
   - **Últimos boletins:** últimos 3 boletins gerados pela API cognitiva
   - **Histórico de eventos:** tabela com eventos solares dos últimos 30 dias (RDS)
3. Criar `src/dashboard/data_loader.py`:
   - Funções de leitura do DynamoDB, RDS, S3 e APIs em tempo real
   - Cache com `@st.cache_data(ttl=300)` para não sobrecarregar os bancos
4. Configurar auto-refresh a cada 5 minutos:
   ```python
   import streamlit as st
   from streamlit_autorefresh import st_autorefresh
   st_autorefresh(interval=300000)
   ```
5. Criar `src/dashboard/requirements.txt` específico
6. Testar localmente:
   ```bash
   streamlit run src/dashboard/app.py
   ```
7. **Opcional para pódio:** Deploy no Streamlit Community Cloud (gratuito)

**Checklist de conclusão:**
- [ ] Dashboard abre sem erros
- [ ] Previsão LSTM visível no gráfico
- [ ] Imagem solar com detecções YOLO exibida
- [ ] Dados ESP32 atualizando em tempo real
- [ ] Pelo menos 1 boletim gerado visível no dashboard
- [ ] URL pública do Streamlit Cloud (se aplicável)

---

## Diagrama de Arquitetura Geral

```
                    ┌─────────────────────────────────────────────┐
                    │              FONTES DE DADOS                 │
                    │  NASA DONKI API    NOAA SWPC API    SDO IMG  │
                    └──────────────────┬──────────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────────┐
                    │          AWS EVENTBRIDGE (hourly)            │
                    └──────────────────┬──────────────────────────┘
                                       │
              ┌────────────────────────▼────────────────────────┐
              │           Lambda: helios-ingestion               │
              │         (coleta + upload para S3 raw/)           │
              └────────────────────────┬────────────────────────┘
                                       │
              ┌────────────────────────▼────────────────────────┐
              │           Lambda: helios-transform               │
              │              (limpeza + normalização)            │
              └──────┬────────────────────────────┬─────────────┘
                     │                            │
          ┌──────────▼──────────┐      ┌──────────▼──────────────┐
          │  DynamoDB           │      │  RDS PostgreSQL          │
          │  (tempo real)       │      │  (histórico)             │
          └──────────┬──────────┘      └──────────┬──────────────┘
                     │                            │
ESP32/Simulador ─────┤  AWS IoT Core              │
(MQTT)               │                            │
                     │                            │
              ┌──────▼────────────────────────────▼─────────────┐
              │              Lambda: helios-predict              │
              │    LSTM (previsão Kp) + YOLO (manchas solares)   │
              └──────────────────────┬───────────────────────────┘
                                     │
              ┌──────────────────────▼───────────────────────────┐
              │           Lambda: helios-cognitive                │
              │     OpenAI API (boletim) + SNS (alertas)          │
              └──────────────────────┬───────────────────────────┘
                                     │
              ┌──────────────────────▼───────────────────────────┐
              │           Dashboard Streamlit                     │
              │   Previsão · Detecções · Mapa · Boletins · IoT   │
              └──────────────────────────────────────────────────┘
```

---

## Regras de Execução para o Agente

1. **Uma fase por vez** — não avançar sem checklist da fase anterior completo
2. **Nunca commitar credenciais** — usar `.env` e verificar `.gitignore` antes de cada commit
3. **Testar cada componente isoladamente** antes de integrá-lo ao pipeline
4. **Nomear recursos AWS** sempre com prefixo `helios-` para fácil identificação e cleanup
5. **Documentar decisões técnicas** em `docs/decisoes_tecnicas.md` ao final de cada fase
6. **Commit ao final de cada fase** com mensagem padronizada: `feat(faseN): descrição`

---

## Recursos de Dados Gratuitos

| Recurso | URL | Formato |
|---|---|---|
| NASA DONKI (eventos solares) | `https://api.nasa.gov/DONKI/` | JSON |
| NOAA Kp em tempo real | `https://services.swpc.noaa.gov/json/planetary_k_index_1m.json` | JSON |
| NOAA Kp histórico | `https://www.ngdc.noaa.gov/stp/GEOMAG/kp_ap.html` | TXT/CSV |
| SDO imagens recentes | `https://sdo.gsfc.nasa.gov/assets/img/latest/` | JPEG |
| SolarNet dataset anotado | `https://github.com/observethesun/SolarNet` | ZIP |
| NOAA Solar Cycle | `https://services.swpc.noaa.gov/json/solar-cycle/` | JSON |

---

## Estrutura de Custos AWS (Free Tier)

| Serviço | Limite Free Tier | Uso Estimado no Projeto | Custo |
|---|---|---|---|
| Lambda | 1M invocações/mês | ~720/mês (1/hora) | $0,00 ✅ |
| EventBridge | 14M eventos/mês | ~720/mês | $0,00 ✅ |
| S3 | 5 GB storage + 2.000 PUTs | ~50 MB/mês | $0,00 ✅ |
| DynamoDB on-demand | 25 GB + 25 WCU/RCU | < 1 GB | ~$0,30/mês ✅ |
| RDS db.t3.micro | 750h/mês free tier | 720h/mês se ligado contínuo | **⚠ ~$15–20/mês** |
| IoT Core | 500K mensagens/mês | ~2.880/mês | $0,08/mês ✅ |
| SNS | 1M publicações/mês | < 100 | $0,00 ✅ |
| API Gateway | 1M chamadas/mês | < 1.000 | $0,00 ✅ |

**Custo estimado extra (fora do free tier):**
- OpenAI API (gpt-4o-mini): ~$0.01–0.05/boletim → custo total negligível
- **Atenção principal: RDS PostgreSQL** — desligar quando não estiver em uso (ver rotina abaixo)

---

## Gestão de Custos — Rotinas de Desligamento

### ⚠ RDS PostgreSQL — desligar após cada sessão de trabalho

O RDS é o único serviço com custo real (~$0,67/dia ligado).
Criar e usar apenas quando necessário; **parar imediatamente após os testes**.

```bash
# Parar instância RDS (cobra só storage ~$0.10/mês enquanto parada)
aws rds stop-db-instance --db-instance-identifier helios-db

# Religar antes de usar (leva ~2 min para ficar disponível)
aws rds start-db-instance --db-instance-identifier helios-db

# Verificar status
aws rds describe-db-instances \
  --db-instance-identifier helios-db \
  --query 'DBInstances[0].DBInstanceStatus' --output text
```

### Lambda e EventBridge — controle de custo zero

As Lambdas não cobram em standby. Porém, para evitar chamadas desnecessárias à
NASA/NOAA fora do período de trabalho ativo, pausar a regra EventBridge:

```bash
# Pausar trigger horário (Lambdas param de ser invocadas automaticamente)
aws events disable-rule --name helios-hourly-trigger

# Reativar quando retomar o desenvolvimento
aws events enable-rule --name helios-hourly-trigger
```

---

## 🔴 Rotina de Descomissionamento Pós-Apresentação

**Data prevista da apresentação:** 2026-06-12
**Data limite para cleanup:** 2026-06-13

Executar na ordem abaixo para encerrar todos os recursos e preservar o crédito restante.

### Passo 1 — Desativar triggers automáticos
```bash
aws events disable-rule --name helios-hourly-trigger
```

### Passo 2 — Parar (ou deletar) o RDS
```bash
# Opção A: parar para preservar dados (continua cobrando storage ~$2/mês)
aws rds stop-db-instance --db-instance-identifier helios-db

# Opção B: deletar permanentemente (sem custo, sem snapshot)
aws rds delete-db-instance \
  --db-instance-identifier helios-db \
  --skip-final-snapshot
```

### Passo 3 — Deletar as Lambdas
```bash
aws lambda delete-function --function-name helios-ingestion
aws lambda delete-function --function-name helios-transform
aws lambda delete-function --function-name helios-predict    # Fase 5
aws lambda delete-function --function-name helios-cognitive  # Fase 8
```

### Passo 4 — Deletar a regra EventBridge e seus targets
```bash
aws events remove-targets --rule helios-hourly-trigger --ids helios-ingestion-target
aws events delete-rule --name helios-hourly-trigger
```

### Passo 5 — Deletar tabelas DynamoDB
```bash
aws dynamodb delete-table --table-name helios-kp-realtime
aws dynamodb delete-table --table-name helios-solar-events  # Fase 4
```

### Passo 6 — Esvaziar e deletar o bucket S3
```bash
# Esvaziar primeiro (S3 não deleta buckets com objetos)
aws s3 rm s3://helios-solar-data --recursive

# Deletar bucket
aws s3 rb s3://helios-solar-data
```

### Passo 7 — Desprovisionar IoT Core (Fase 7)
```bash
# Listar e deletar certificados, políticas e things criados
aws iot list-things --query 'things[*].thingName' --output text
# Seguir com delete-thing, detach-policy, delete-certificate conforme listado
```

### Passo 8 — SNS (Fase 8)
```bash
aws sns list-topics --query 'Topics[*].TopicArn' --output text
# Para cada ARN retornado:
aws sns delete-topic --topic-arn <ARN>
```

### Verificação final
```bash
# Confirmar que não sobrou nada com custo relevante
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Project,Values=helios \
  --query 'ResourceTagMappingList[*].ResourceARN' --output table 2>/dev/null || \
echo "Verificar manualmente: Lambda, RDS, DynamoDB, S3, EventBridge, IoT, SNS"
```

---

## Links Úteis para Documentação do PDF

- Repositório GitHub: `[preencher após criar]`
- Dashboard Streamlit: `[preencher após deploy]`
- Vídeo YouTube (não listado): `[preencher após gravar]`
- NASA DONKI API Docs: `https://kauai.ccmc.gsfc.nasa.gov/DONKI/`
- NOAA SWPC: `https://www.swpc.noaa.gov/`
- SDO NASA: `https://sdo.gsfc.nasa.gov/`
