# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/">
  <img src="./docs/logo-fiap.png" 
       alt="FIAP - Faculdade de Informática e Administração Paulista" 
       width="40%">
</a>
</p>

<br>

# HeliOS — Sistema de Predição de Tempestades Solares e Impacto em Infraestrutura Crítica

## Grupo HeliOS - QUERO CONCORRER

## 👨‍🎓 Integrantes:
- <a href="https://www.linkedin.com/in/daniel-baião-0b351049/">Daniel Emilio Baião</a>
- <a href="https://www.linkedin.com/company/inova-fusca">Erik Criscuolo</a>
- <a href="https://www.linkedin.com/company/inova-fusca">Hugo Rodrigues Carvalho Silva</a>
- <a href="https://www.linkedin.com/company/inova-fusca">Marcus Vinícius Loureiro Garcia</a> 
- <a href="https://www.linkedin.com/company/inova-fusca">Sidney William de Paula Dias</a> 

## 👩‍🏫 Professores:
### Tutor(a)
- <a href="https://www.linkedin.com/in/sabrina-otoni-22525519b/">Sabrina Otoni</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/company/inova-fusca">André Godoi Chiovato</a>


## 📜 Descrição

O **HeliOS** é um sistema inteligente de monitoramento e predição de tempestades solares com foco em proteger infraestruturas críticas terrestres — como redes elétricas, satélites de comunicação e sistemas de navegação — de eventos de clima espacial extremo.

Tempestades geomagnéticas causadas por Ejeções de Massa Coronal (CMEs) e Flares Solares podem induzir correntes elétricas destrutivas em transformadores de alta tensão, corromper sinais de GPS e perturbar redes de telecomunicações. O evento de Carrington (1859) e a tempestade de Quebec (1989) demonstraram que esses fenômenos têm potencial catastrófico — e hoje a dependência da humanidade em infraestrutura digital torna o risco ainda maior.

O HeliOS combina dados espaciais reais das APIs da **NASA (DONKI)** e da **NOAA (Space Weather Prediction Center)** com modelos de inteligência artificial para:

1. **Prever** o índice de perturbação geomagnética Kp com até 6 horas de antecedência usando uma rede **LSTM** treinada com dados históricos desde 1932.
2. **Detectar e classificar** manchas solares em imagens do Observatório de Dinâmica Solar (SDO/NASA) usando **YOLO**, identificando regiões ativas com maior probabilidade de erupção.
3. **Ingerir dados em tempo real** via pipeline serverless na **AWS** (S3 + Lambda + EventBridge), armazenando eventos em **DynamoDB** (tempo real) e **RDS PostgreSQL** (histórico).
4. **Simular sensores físicos** com um **ESP32** que emula um magnetômetro terrestre, transmitindo leituras via **MQTT** para AWS IoT Core.
5. **Emitir alertas em linguagem natural** usando a **API OpenAI**, gerando boletins automáticos distribuídos por **SNS** (SMS/e-mail) quando o índice Kp ultrapassa limiares críticos.
6. **Visualizar** o estado do sistema em tempo real via dashboard **Streamlit**.

A solução demonstra como IA aplicada a dados espaciais pode antecipar desastres naturais de origem solar, oferecendo janelas de tempo para que operadores de infraestrutura tomem medidas preventivas — como desligar transformadores vulneráveis ou reorientar satélites — antes que a tempestade geomagnética atinja a Terra.


## 📁 Estrutura de pastas

```
Global-Solution-2/
├── README.md                        # Este arquivo
├── requirements.txt                 # Dependências Python do projeto
├── .env.example                     # Variáveis de ambiente necessárias (sem valores reais)
├── data/
│   ├── raw/donki/                   # Eventos solares brutos da NASA DONKI API
│   ├── raw/kp/                      # Índice Kp em tempo real da NOAA
│   ├── processed/                   # Dados tratados para treino do LSTM
│   └── solar_images/                # Imagens SDO para detecção YOLO
├── src/
│   ├── ingestion/                   # Scripts de coleta de dados
│   ├── pipeline/                    # Lambdas e pipeline AWS
│   ├── database/                    # Setup SQL/NoSQL
│   ├── ml/
│   │   ├── lstm/                    # Modelo de previsão Kp
│   │   └── yolo/                    # Detecção de manchas solares
│   ├── iot/                         # Código ESP32 + MQTT
│   ├── cognitive/                   # API cognitiva + SNS
│   └── dashboard/                   # Streamlit
└── docs/
    ├── arquitetura.png              # Diagrama da solução
    ├── fluxograma.png               # Fluxo de dados
    └── decisoes_tecnicas.md         # Registro de decisões de arquitetura
```

## 📎 Links e Observações

- **Repositório GitHub:** https://github.com/agentesiafiap/tiao-2026
- **APIs utilizadas:** [NASA DONKI](https://api.nasa.gov/) | [NOAA SWPC](https://www.swpc.noaa.gov/) | [SDO NASA](https://sdo.gsfc.nasa.gov/)
- **Decisões técnicas:** ver [docs/decisoes_tecnicas.md](docs/decisoes_tecnicas.md)
- Este projeto **aceita** participação na competição Global Solution FIAP 2026.1.


## 🔧 Como executar o código

### Pré-requisitos

| Ferramenta | Versão mínima | Instalação |
|---|---|---|
| Python | 3.10+ | [python.org](https://www.python.org/) |
| AWS CLI | 2.x | `pip install awscli` |
| Git | 2.x | [git-scm.com](https://git-scm.com/) |
| Arduino IDE | 2.x (opcional) | [arduino.cc](https://www.arduino.cc/) |

### Configuração do ambiente

```bash
# 1. Clonar o repositório
git clone https://github.com/agentesiafiap/tiao-2026.git
cd tiao-2026/1TIAO/Global-Solution-2

# 2. Criar e ativar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas credenciais reais

# 5. Verificar conexão AWS
aws sts get-caller-identity
```

### Executar ingestão de dados

```bash
python src/ingestion/run_all.py
```

### Treinar modelo LSTM — Google Colab (recomendado)

> O treinamento local no macOS ARM com TF 2.21 tem um bug de XLA que congela na época 1.
> Use o Google Colab com GPU T4 (~5 min):

1. Abrir `src/ml/lstm/gs2_helios.ipynb` no Google Colab
2. Ativar GPU: Ambiente de execução → Alterar tipo → T4 GPU
3. Executar todas as células
4. Baixar `helios_lstm.keras` e `scaler.pkl` → colocar em `src/ml/lstm/model/`

```bash
# Executar inferência após ter o modelo treinado
python src/ml/lstm/predict.py --output json
```

### Treinar modelo YOLO — Google Colab (recomendado)

1. Abrir `src/ml/yolo/colab_yolo.ipynb` no Google Colab com GPU T4
2. Executar todas as células (dataset sintético gerado automaticamente)
3. Baixar `helios_yolo.pt` → colocar em `src/ml/yolo/model/`

```bash
# Executar detecção na última imagem SDO
python src/ml/yolo/inference.py --latest
```

### Simular sensor ESP32 / IoT

```bash
# Modo normal (Kp baixo, campo magnético estável)
python src/iot/simulate_esp32.py --count 10 --interval 2

# Modo tempestade (Kp ~5.8, STORM_MAJOR)
python src/iot/simulate_esp32.py --storm --count 5
```

### Gerar boletim cognitivo

```bash
# Boletim normal
python src/cognitive/bulletin_generator.py

# Boletim de emergência (simula tempestade + dispara SNS)
python src/cognitive/bulletin_generator.py --storm
```

### Iniciar dashboard

```bash
streamlit run src/dashboard/app.py
# Acesse: http://localhost:8501
```

## 🛠 Tecnologias Utilizadas

| Camada | Tecnologia | Uso |
|---|---|---|
| **Machine Learning** | TensorFlow/Keras LSTM | Previsão de SSN (manchas solares) 6 meses |
| **Visão Computacional** | YOLOv8 (Ultralytics) | Detecção de manchas em imagens SDO |
| **Cloud** | AWS Lambda | Pipeline serverless de ingestão e cognitivo |
| **Cloud** | AWS DynamoDB | Armazenamento em tempo real (Kp, eventos) |
| **Cloud** | AWS S3 | Dados brutos, modelos, boletins, imagens |
| **Cloud** | AWS SNS | Alertas por e-mail quando Kp ≥ 5 |
| **Cloud** | AWS EventBridge | Triggers automáticos (1h ingestão, 6h cognitivo) |
| **Cloud** | AWS RDS PostgreSQL | Histórico estruturado de eventos solares |
| **IoT** | ESP32 + QMC5883L | Magnetômetro físico (firmware Arduino C++) |
| **IoT** | MQTT / HiveMQ | Transmissão de leituras do sensor |
| **Cognitivo** | OpenAI gpt-4o-mini | Geração de boletins em linguagem natural |
| **Cognitivo** | AWS Bedrock Claude | Fallback para geração de boletins |
| **Dashboard** | Streamlit + Plotly | Visualização interativa em tempo real |
| **Dashboard** | Folium | Mapa global de zonas de risco auroral |
| **Dados** | NASA DONKI API | Eventos solares (CME, flares) |
| **Dados** | NOAA SWPC API | Índice Kp em tempo real |
| **Dados** | SDO/AIA NASA | Imagens solares para detecção YOLO |

## 🗃 Histórico de lançamentos

* 1.0.0 - 05/06/2026
    * Fase 9: Dashboard Streamlit com integração completa
* 0.9.0 - 05/06/2026
    * Fase 8: API Cognitiva (boletins automáticos) + Lambda + SNS alertas
* 0.8.0 - 05/06/2026
    * Fase 7: IoT — simulador ESP32, MQTT HiveMQ, DynamoDB
* 0.7.0 - 05/06/2026
    * Fase 6: YOLOv8 fine-tuning, mAP50=0.866 (Google Colab T4)
* 0.6.0 - 05/06/2026
    * Fase 5: LSTM treinado (MAE ~12 SSN, Google Colab T4)
* 0.4.0 - 04/06/2026
    * Fase 4: DynamoDB + RDS PostgreSQL schema e seed
* 0.3.0 - 04/06/2026
    * Fase 3: Lambda helios-ingestion + helios-transform + EventBridge
* 0.2.0 - 04/06/2026
    * Fase 2: Scripts de ingestão NASA DONKI, NOAA Kp, imagens SDO
* 0.1.0 - 04/06/2026
    * Fase 1: Setup do repositório, estrutura de pastas, README e ambiente base

---


## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/SabrinaOtoni/TEMPLATE-FIAP-GRAD-ON-IA">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
