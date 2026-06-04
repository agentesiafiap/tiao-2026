# HeliOS — Registro de Decisões Técnicas

> Documento vivo: atualizado ao longo de todas as fases do projeto.

---

## ADR-001 — Linguagem principal: Python

**Status:** Aceito  
**Data:** 2026-06-04

**Contexto:** Necessidade de uma linguagem que suporte manipulação de dados, ML, integração com AWS e desenvolvimento rápido.

**Decisão:** Python 3.11 como linguagem primária em todo o projeto.

**Consequências:** Ecossistema rico (boto3, tensorflow, ultralytics, streamlit). Trade-off: performance inferior a Go/Rust para workloads de alta frequência, mas aceitável para os volumes do projeto.

---

## ADR-002 — Armazenamento: DynamoDB + RDS (dual-store)

**Status:** Aceito  
**Data:** 2026-06-04

**Contexto:** Dados de sensores têm natureza de série temporal de alta frequência (leituras a cada minuto). Dados históricos de eventos precisam de queries relacionais complexas.

**Decisão:** 
- **DynamoDB** para leituras em tempo real do ESP32 e índice Kp (baixa latência de escrita, TTL automático de 7 dias).
- **RDS PostgreSQL** para histórico de eventos DONKI e resultados de predição do LSTM (queries SQL, JOINs).

**Consequências:** Complexidade operacional maior, mas cada banco é usado no seu ponto forte.

---

## ADR-003 — LSTM para predição de Kp (não Transformer)

**Status:** Aceito  
**Data:** 2026-06-04

**Contexto:** Previsão de série temporal do índice Kp com janela deslizante de 24h de entrada e horizonte de 6h de saída.

**Decisão:** LSTM bidirecional com dropout, implementado em TensorFlow/Keras. Transformers foram considerados mas rejeitados por custo computacional no free tier AWS.

**Consequências:** Menor capacidade de capturar dependências de longo prazo, mas treinamento viável em CPU no free tier. Reavaliação prevista na Fase 5.

---

## ADR-004 — YOLOv8 para detecção de manchas solares

**Status:** Aceito  
**Data:** 2026-06-04

**Contexto:** Detecção e classificação de manchas solares em imagens do SDO em resolução 512x512.

**Decisão:** YOLOv8n (nano) via `ultralytics`. Fine-tuning sobre dataset público de manchas solares (SPoCA/HELIO).

**Consequências:** Modelo leve o suficiente para inferência em Lambda com container Docker. Precisão inferior ao YOLOv8x, mas viável para prova de conceito.

---

## ADR-005 — ESP32 com simulação Python como fallback

**Status:** Aceito  
**Data:** 2026-06-04

**Contexto:** Nem todos os ambientes de execução terão hardware ESP32 físico disponível.

**Decisão:** Implementar `src/iot/esp32_simulator.py` que publica via MQTT as mesmas mensagens que o firmware do ESP32 real, permitindo execução completa do pipeline sem hardware.

**Consequências:** Demo 100% executável em ambiente de software. O firmware `.ino` real também será entregue para validação com hardware físico.

---

## ADR-006 — OpenAI API para boletins (com fallback Bedrock)

**Status:** Aceito  
**Data:** 2026-06-04

**Contexto:** Geração de boletins de alerta em linguagem natural a partir de dados estruturados de tempestade.

**Decisão:** OpenAI GPT-4o-mini como primário. Amazon Bedrock (Claude Haiku) como fallback quando `OPENAI_API_KEY` não estiver configurada.

**Consequências:** Custo mínimo (GPT-4o-mini ~$0.15/1M tokens). Fallback garante funcionamento dentro do free tier AWS.

---
