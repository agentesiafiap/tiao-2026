<img src="../assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width=30% height=30%>

# AI Project Document - Fase 2 - FIAP

## FarmTech Solutions - Sistema de Irrigação Inteligente

#### Erik Criscuolo, Daniel Emilio Baião, Marcus Vinícius Loureiro Garcia, Sidney William de Paula Dias, Hugo Rodrigues Carvalho Silva

## Sumário

[1. Introdução](#c1)

[2. Visão Geral do Projeto](#c2)

[3. Desenvolvimento do Projeto](#c3)

[4. Resultados e Avaliações](#c4)

[5. Conclusões e Trabalhos Futuros](#c5)

[6. Referências](#c6)

[Anexos](#c7)

<br>

# <a name="c1"></a>1. Introdução

## 1.1 Escopo do Projeto

A **FarmTech Solutions** tem como objetivo aplicar tecnologias de **Inteligência Artificial e IoT** para modernizar o cultivo de café, promovendo automação e sustentabilidade no uso de recursos naturais.

O projeto propõe o desenvolvimento de um **sistema de irrigação automatizado e inteligente** utilizando o **ESP32**, sensores de **Umidade, NPK e pH**, e integração com **pipelines de Data Science** e **API meteorológica**.

## 1.2 Contexto da Inteligência Artificial

A IA desempenha papel essencial na agricultura moderna, especialmente no **monitoramento e controle de variáveis ambientais**. Através da coleta e análise automatizada de dados, é possível aprimorar decisões de irrigação, nutrição e manejo das culturas.

<br>

# <a name="c2"></a>2. Visão Geral do Projeto

## 2.1 Objetivos do Projeto

Desenvolver um sistema automatizado de irrigação para o cultivo de café, com base na coleta de dados ambientais e integração de análise estatística e previsão climática.

## 2.2 Público-Alvo

Produtores rurais, cooperativas e empresas agrícolas que buscam soluções tecnológicas para aumentar a eficiência, reduzir custos e melhorar a qualidade do cultivo.

## 2.3 Metodologia

1. Definição de requisitos e lógica de decisão da irrigação.
2. Implementação de sensores simulados no Wokwi/VS Code.
3. Integração com scripts Python, Bash e R.
4. Execução de pipeline automatizado de análise de dados.
5. Avaliação dos resultados e ajustes finais.

<br>

# <a name="c3"></a>3. Desenvolvimento do Projeto

## 3.1 Lógica de Irrigação e Decisão

O sistema aciona o **relé da bomba de irrigação** apenas quando **todas as condições ideais forem atendidas**:

- **Umidade do solo < 60%**
- **N, P e K presentes** (botões pressionados)
- **pH entre 5.5 e 6.5**
- **Sem bloqueio externo ativo** (condição meteorológica favorável)

| Elemento | Requisito da Lógica | Simulação no Wokwi |
|-----------|--------------------|--------------------|
| Nitrogênio (N) | Presente (true) | Botão N pressionado |
| Fósforo (P) | Presente (true) | Botão P pressionado |
| Potássio (K) | Presente (true) | Botão K pressionado |
| pH (LDR) | 5.5–6.5 | Potenciômetro do LDR |
| Umidade (DHT22) | < 60% | Slider do DHT22 |
| Bloqueio Externo | Ausente (0) | Serial Remoto (Python) |

<br>

## 3.2 Tecnologias Utilizadas

- **Hardware:** ESP32 DevKit V1 (simulado no Wokwi)
- **Sensores:** DHT22 (umidade), LDR (pH), Botões (NPK), Relé (bomba d’água)
- **Linguagens:** C/C++, Python, R, Bash
- **Ambiente:** PlatformIO, VS Code, Wokwi Simulator

![Diagrama de Conexões](../assets/conexoes.png)

<br>

## 3.3 Pipeline Automatizado de Data Science

O projeto implementa um **pipeline automatizado** para coleta, análise e integração de dados entre **ESP32, Python, Bash e R**.

### Integração com API Pública (Open-Meteo)

- Suspende a irrigação em caso de previsão de chuva.
- Scripts Python (`api_weather.py`) e Bash (`run_analysis.sh`) automatizam o envio do bloqueio ao ESP32 via porta serial remota.

### Análise Estatística em R

- Calcula **índices de deficiência do solo** com base em logs do ESP32.
- Usa scripts Python para capturar, limpar e preparar os dados (`log_capturer.py`, `data_cleaner.py`).
- O script R (`data_analysis.R`) realiza a análise e gera o **score de deficiência**.

### Orquestração do Pipeline

O script **`run_analysis.sh`** automatiza as etapas:
1. Executa a API de previsão e envia dados ao ESP32.
2. Captura logs da simulação.
3. Limpa e transforma os dados.
4. Executa análise estatística final em R.

Execução:
```bash
chmod +x run_analysis.sh
./run_analysis.sh
```

<br>

# <a name="c4"></a>4. Resultados e Avaliações

## 4.1 Resultados Obtidos

O sistema mostrou **eficiência e precisão** na simulação, acionando a irrigação automaticamente apenas quando necessário e respondendo corretamente às condições de solo e clima.

## 4.2 Feedback

Os testes demonstraram que o modelo pode ser facilmente adaptado para uso real, com potencial de redução no consumo de água e melhoria na produtividade.

<br>

# <a name="c5"></a>5. Conclusões e Trabalhos Futuros

O projeto **atingiu seus objetivos**, mostrando a viabilidade de integrar IoT, IA e Data Science na agricultura.

**Trabalhos futuros incluem:**
- Integração com plataformas de nuvem (IoT remoto).
- Interface web para monitoramento.
- Expansão para outras culturas agrícolas.

<br>

# <a name="c6"></a>6. Referências

- Open-Meteo API Documentation  
- ESP32 PlatformIO Docs  
- Artigos técnicos sobre irrigação inteligente e Data Science aplicada à agricultura

<br>

# <a name="c7"></a>Anexos

## A. Estrutura de Arquivos

| Arquivo/Pasta | Descrição | Status |
|----------------|------------|---------|
| `README.md` | Documentação principal | Completo |
| `platformio.ini` | Configuração do ESP32 | Entregue |
| `wokwi.toml` | Configuração da simulação | Entregue |
| `diagram.json` | Diagrama de conexões | Entregue |
| `src/main.cpp` | Código principal (C++) | Entregue |
| `script/python_api/api_weather.py` | Lógica de chuva | Entregue |
| `script/r_analysis/data_analysis.R` | Análise estatística | Entregue |
| `script/r_analysis/log_capturer.py` | Captura de logs | Entregue |
| `script/r_analysis/data_cleaner.py` | Limpeza e integração | Entregue |
| `run_analysis.sh` | Orquestrador do pipeline | Entregue |

## B. Demonstração em Vídeo

[Link do vídeo (YouTube - Não listado)](https://youtu.be/pz6-2eiDTZE)
