# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# FarmTech Solutions - Hub Central (Fase 7)

## Agentes IA FIAP

## 👨‍🎓 Integrantes: 
- <a href="">Daniel Emilio Baião</a>
- <a href="">Erik Criscuolo</a>
- <a href="">Marcus Vinícius Loureiro Garcia</a> 
- <a href="">Sidney William de Paula Dias,</a> 
- <a href="">Hugo Rodrigues Carvalho Silva</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/in/sabrina-otoni-22525519b/">Sabrina Otoni</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/company/inova-fusca">André Godoi Chiovato</a>

## 📜 Descrição

O **FarmTech Solutions** evoluiu de um simples sistema de monitorização agrícola para um ecossistema digital inteligente de alto valor agregado. O objetivo desta entrega final é consolidar os serviços desenvolvidos ao longo do curso numa plataforma centralizada e *Production-Ready*, construída com arquitetura monolítica modular focada no utilizador final.

Através de um painel interativo orquestrador em **Python (Streamlit)**, o sistema integra:
1. **Modelagem e Estatística (R):** Cálculos de manejo de insumos e consumo de APIs meteorológicas.
2. **IoT e Banco de Dados (Oracle):** Leitura de logs físicos (ESP32) e gestão automatizada de tabelas relacionais (`DADO_AGRICOLA`).
3. **Machine Learning (Scikit-Learn):** Análise exploratória (Clusterização/PCA) e regressão preditiva para rendimento de safras, gerando recomendações automáticas de irrigação e fertilização.
4. **Visão Computacional Avançada (YOLOv5):** Prova de Conceito (PoC) expandida para duas novas verticais estratégicas:
   * 🐶 **Saúde Animal:** Diagnóstico e monitoramento clínico veterinário (Alvo: *Shih Tzu* - Stress test de texturas/pelagem).
   * 🚙 **Segurança Patrimonial:** Controle de acesso restrito (Alvo: *Nissan Kicks* - Validação de design automotivo).
5. **Cloud Computing (AWS SNS):** Disparo de alertas em tempo real (E-mail/SMS) integrados aos gatilhos de Machine Learning e Visão Computacional.

---

## 🔗 Histórico de Fases (Repositórios Anteriores)
A evolução iterativa deste ecossistema pode ser rastreada através das entregas prévias da equipe:
* **Fase 01 (Base de Dados e R):** [farmtech-fiap-cap01](https://github.com/hugorcsilva/farmtech-fiap-cap01)
* **Fase 02 (IoT ESP32 e Python):** [fase2-grupo9-esp32](https://github.com/agentesiafiap/cursotiaos-fase2-grupo9-esp32) | [fase2-grupo6-python](https://github.com/agentesiafiap/cursotiaos-fase2-grupo6-python)
* **Fase 03 (Oracle Database):** [fase3-grupo16-oracle](https://github.com/agentesiafiap/cursotiaos-fase3-grupo16-oracle)
* **Fase 04 (Machine Learning e EDA):** [fase4-grupo43-previsao](https://github.com/agentesiafiap/cursotiaos-fase4-grupo43-previsao)
* **Fase 05 (Cloud AWS):** [fase5-grupo19-ml-aws](https://github.com/agentesiafiap/cursotiaos-fase5-grupo19-ml-aws)
* **Fase 06 (Visão Computacional YOLO):** [fase6-grupo21-yolo-cnn](https://github.com/agentesiafiap/cursotiaos-fase6-grupo21-yolo-cnn)

---

## 🏗️ Arquitetura e MLOps
Para garantir compatibilidade universal entre os computadores dos avaliadores, o projeto foi empacotado utilizando as melhores práticas de MLOps:
* **Docker & Docker Compose:** Contêiner imutável forçado na arquitetura `x86_64` (`linux/amd64`).
* **Instalador UV:** Utilização do `uv` (Rust) para instalação ultrarrápida de dependências Python.
* **R Pré-Compilado:** Uso de binários Debian (`r-cran-httr`, `r-cran-jsonlite`) para evitar gargalos de compilação C/C++ na nuvem.
* **PyTorch CPU-Only:** Redução drástica do peso da imagem utilizando `extra-index-url` sem dependência de CUDA.

### Estrutura de Diretórios

```text
/
├── docker-compose.yml            # Orquestrador de serviços
├── Dockerfile                    # Receita da imagem x86 (Python + R + YOLO)
├── app.py                        # Dashboard Principal (Hub Streamlit)
├── requirements.txt              # Dependências Python ultra-otimizadas
├── .env.example                  # Template de variáveis de ambiente
├── yolov5_farmtech.pt            # Pesos treinados do YOLOv5 (60 épocas)
├── regression_model.joblib       # Modelo de ML supervisionado (Fase 4)
│
├── data/                         # Volume persistente
    |── dados_historicos_2024.csv # Logs físicos do IoT para importação Oracle
    |── crop_yield.csv            # Base histórica para análise de clusters
    |── dados_farmtech.csv        # Armazenamento de áreas de plantio
    |── confusion_matrix.png      # Métricas do modelo YOLO     
    |── F1_curve.png              # Métricas do modelo YOLO
│
└── scripts/                      # Scripts analíticos independentes
    ├── analise_estatistica.R     # Motor estatístico (Fase 1)
    ├── analise_openmeteo.R       # Meteorologia via R (Fase 1)    
    └── recommend.py              # Regras de negócio para irrigação e fertilização (Fase 4)
```

##🚀Como Executar o Projeto Localmente

**Pré-requisitos:** Certifique-se de ter o **Docker Desktop** instalado em sua máquina. A execução conteinerizada do projeto (via `docker-compose`) descarta a necessidade de configurações manuais e instalações locais do Python e do R.

* Clone este repositório.

* **Configuração de Variáveis de Ambiente:** Crie um arquivo `.env` na raiz do projeto contendo suas credenciais do Oracle e da AWS (use o `.env.example` como base)::

```.env
DB_USER=seu_usuario
DB_PASS=sua_senha
DB_HOST=seu_host_oracle
DB_PORT=1521
DB_SERVICE=seu_service_name

AWS_ACCESS_KEY_ID=sua_chave_aws
AWS_SECRET_ACCESS_KEY=seu_secret_aws
AWS_DEFAULT_REGION=us-east-1
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:1234567890:SeuTopico
```

* Abra o terminal na pasta do projeto e inicie o ambiente orquestrado:

```Bash
docker-compose up --build
```

* Assim que o terminal indicar que o Streamlit foi iniciado, acesse no seu navegador:
👉 `http://localhost:8501`

Para desligar a aplicação e limpar a memória do terminal, pressione Ctrl + C e, opcionalmente, rode `docker-compose down`.

## ☁️ Comprovação da Infraestrutura Cloud (AWS SNS)

O sistema possui gatilhos inteligentes configurados para disparar ações de contingência (irrigação de emergência ou alertas de segurança/clínicos) direto para o celular da equipe.
(Substituir pelos prints da AWS e da caixa de entrada/SMS)

## 🎥 Pitch e Apresentação do Sistema
Vídeo demonstrativo (até 10 minutos) comprovando o funcionamento de todas as Fases e da integração em contêiner:

👉 [Link para o Vídeo no YouTube (Não Listado)](https://youtu.be/aXUJDpewup4)

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>