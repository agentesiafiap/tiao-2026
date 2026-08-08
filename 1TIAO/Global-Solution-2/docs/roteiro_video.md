# 🎬 Roteiro — Vídeo de Apresentação HeliOS (5 min)

**Global Solution 2026.1 — FIAP**
**Grupo HeliOS:** Daniel Baião, Erik Criscuolo, Hugo Rodrigues, Marcus Vinícius, Sidney William

---

## [0:00–0:20] — Abertura

> *Tela: Logo HeliOS + título animado*

**Narração:**
"HeliOS — Sistema de Predição de Tempestades Solares. FIAP Global Solution 2026.1. Grupo HeliOS: Daniel Baião, Erik Criscuolo, Hugo Rodrigues, Marcus Vinícius e Sidney William. **QUERO CONCORRER.**"

---

## [0:20–0:50] — O Problema

> *Tela: imagem do Sol em erupção + notícia de apagão Quebec 1989*

**Narração:**
"Tempestades solares destroem transformadores, derrubam GPS e interrompem comunicações. O evento de Quebec em 1989 deixou 6 milhões de pessoas sem energia em 90 segundos. "
"A materia em tela é mais recente. De 05 de junho. Mostra que uma gigantesca nuvem de plasma e campos magnéticos foi lançada pelo Sol após uma sequência de erupções. Durante a viagem pelo espaço, uma ejeção de massa coronal mais rápida alcançou e absorveu outra mais lenta, formando o chamado “CME canibal”. Ao atingir a Terra, essa estrutura pode provocar tempestades geomagnéticas capazes de intensificar auroras em regiões incomuns, além de causar interferências temporárias em satélites, sistemas de navegação, comunicações por rádio e redes elétricas. Este evento demonstra como a atividade do Sol pode impactar diretamente a infraestrutura tecnológica do planeta — E uma similaridade assustadora entre o evento de 1989 e este: e a humanidade ainda reage, em vez de se antecipar."
---

## [0:50–1:20] — A Solução

> *Tela: diagrama de arquitetura HeliOS*

**Narração:**
"O HeliOS integra 9 tecnologias para transformar reação em antecipação: coleta dados reais da NASA e NOAA (National Oceanic and Atmospheric Administration - Agência dos EUA que monitora oceanos, atmosfera e clima espacial), treina IA para prever tempestades, detecta manchas solares em imagens do Sol, monitora o campo magnético terrestre via IoT, gera alertas automáticos em linguagem natural e exibe tudo em um dashboard em tempo real."

---

## [1:20–2:00] — Machine Learning: LSTM + YOLO

> *Tela: gráfico de previsão LSTM no dashboard + imagem SDO com bounding boxes*

**Narração:**
"Dois modelos de IA em produção. O LSTM — treinado no Google Colab com GPU T4 em dados de manchas solares desde 1932 — prevê a atividade solar para os próximos 6 meses com erro médio de 12 SSN (SunSpot Number). O YOLOv8, fine-tunado com dataset sintético, detecta regiões ativas e grupos de manchas em imagens do Observatório Solar SDO da NASA — com mAP50 de 0.866. (mean Average Precision) "

---

## [2:00–2:30] — Pipeline AWS

> *Tela: console AWS mostrando Lambda, DynamoDB, S3, EventBridge*

**Narração:**
"Todo o pipeline roda serverless na AWS. EventBridge aciona Lambdas a cada hora para ingerir dados da NASA DONKI e NOAA. O DynamoDB armazena leituras em tempo real com TTL de 7 dias. O RDS PostgreSQL guarda o histórico estruturado. E o S3 centraliza dados brutos, modelos treinados e boletins gerados."

---

## [2:30–3:00] — IoT: ESP32 Magnetômetro

> *Tela: terminal mostrando simulate_esp32.py em execução + DynamoDB com itens*

**Narração:**
"O componente IoT simula um magnetômetro ESP32 com sensor QMC5883L. Em modo normal, lê o campo geomagnético de São Paulo — 23.000 nanoteslas. Em modo tempestade, o campo cai para 20.000 nT e o índice Kp sobe para 5.8. As leituras chegam via MQTT ao HiveMQ e são gravadas diretamente no DynamoDB."

---

## [3:00–3:30] — API Cognitiva + SNS

> *Tela: terminal mostrando bulletin_generator.py --storm + e-mail de alerta recebido*

**Narração:**
"A API Cognitiva combina previsão LSTM, detecções YOLO e dados IoT para gerar boletins técnicos em português. Quando o Kp previsto ultrapassa 5.0, a Lambda helios-cognitive dispara um alerta via SNS — que chega por e-mail em segundos. Isso demonstra integração real entre IA generativa, pipeline de dados e notificação de infraestrutura crítica."

---

## [3:30–4:30] — Dashboard ao Vivo

> *Tela: dashboard Streamlit aberto no browser, demonstrando cada seção*

**Narração:**
"O dashboard consolida tudo. Aqui vemos: o status geomagnético atual baseado nos dados NOAA — índice Kp e campo B nas últimas horas. A previsão LSTM para os próximos 6 meses com banda de confiança. A última imagem do Sol com detecções YOLO anotadas. O mapa mundial com zonas de risco auroral — destacando o Ártico, Escandinávia e a estação HeliOS em São Paulo. Os últimos boletins gerados pela IA. E o histórico de CMEs da NASA dos últimos 30 dias. Tudo atualizado automaticamente a cada 5 minutos."

---

## [4:30–5:00] — Conclusão

> *Tela: logo HeliOS + lista de tecnologias integradas*

**Narração:**
"HeliOS demonstra que é possível integrar Machine Learning, visão computacional, IoT, computação serverless, IA cognitiva e visualização em tempo real para resolver um problema real de segurança de infraestrutura crítica. Dados reais. Modelos treinados. Pipeline em produção. Dashboard funcional. FIAP Global Solution 2026.1 — Grupo HeliOS."

---

## ✅ Checklist antes de gravar

- [ ] Abrir dashboard em `http://localhost:8501` e deixar visível
- [ ] Ter terminal pronto com `python src/cognitive/bulletin_generator.py --storm`
- [ ] Ter e-mail de alerta SNS já recebido para mostrar
- [ ] Mostrar console AWS (Lambda, DynamoDB, S3)
- [ ] Gravar em resolução mínima 1080p
- [ ] Publicar como **"Não listado"** no YouTube
- [ ] Incluir link no PDF na última página

---

## 🖥️ Comandos para demonstração ao vivo

```bash
# Ativar ambiente
cd tiao-2026/1TIAO/Global-Solution-2
source .venv/bin/activate

# 1. Subir dashboard
streamlit run src/dashboard/app.py

# 2. Simular sensor ESP32 (modo normal)
python src/iot/simulate_esp32.py --count 5 --interval 2

# 3. Simular tempestade + disparar alerta SNS
python src/cognitive/bulletin_generator.py --storm

# 4. Previsão LSTM
python src/ml/lstm/predict.py --output json

# 5. Detecção YOLO na última imagem solar
python src/ml/yolo/inference.py --latest
```
