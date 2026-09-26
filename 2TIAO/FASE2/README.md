# CardioIA 🫀🤖 — Fase 2: Diagnóstico Automatizado

**Projeto:** Simulação de Ecossistema de Cardiologia Moderna com IA
**Fase 2:** Diagnóstico Automatizado — IA no Estetoscópio Digital
**Grupo 20** — Daniel Emilio Baião (rm567686) · Hugo Rodrigues (rm566891)

Escopo desta entrega: **Parte 1** (extração de sintomas) e **Parte 2** (classificador de risco).

---

## Parte 1 — Frases de sintomas + extração de informações

- [`assets/frases_sintomas.txt`](assets/frases_sintomas.txt) — 10 frases de pacientes, cobrindo 6 doenças (Infarto, Angina, Insuficiência Cardíaca, Arritmia, Hipertensão, AVC).
- [`assets/mapa_conhecimento.csv`](assets/mapa_conhecimento.csv) — 32 linhas (`sintoma_1, sintoma_2, doenca_associada`), com sinônimos por doença.
- [`src/extracao_diagnostico.py`](src/extracao_diagnostico.py) — lê as frases, normaliza texto (minúsculas + remoção de acentos) e identifica sintomas por **matching de conjunto de palavras** (mais robusto que substring exata a variações de conjugação); sugere o diagnóstico por contagem de votos por doença, tratando os casos de nenhum sintoma identificado e de empate.

**Execução:**
```bash
python3 src/extracao_diagnostico.py
```
Resultado: as 10 frases geram diagnóstico coerente com a doença pretendida (sem casos sem match).

## Parte 2 — Classificador de risco (baixo risco / alto risco)

- [`assets/base_risco.csv`](assets/base_risco.csv) — 60 frases balanceadas (30/30), com ~13% de casos ambíguos propositais (sintoma "gatilho" em contexto benigno, ou sintoma brando em contexto de risco).
- [`notebooks/classificador_risco.ipynb`](notebooks/classificador_risco.ipynb) — TF-IDF (`TfidfVectorizer`) + split 80/20 estratificado + treino/comparação de `LogisticRegression` e `DecisionTreeClassifier`.

**Resultado obtido:** Decision Tree (92% de acurácia) superou Logistic Regression (75%) no split de teste (12 frases). O notebook testa o modelo escolhido com 4 frases inéditas e discute um erro observado (frase de dor lombar banal classificada como alto risco), atribuído ao vocabulário limitado da base de treino — ver seção final do notebook.

---

## Auditoria de insumos e governança de dados

Os insumos da Fase 1 (dataset numérico categórico e corpus de textos/diretrizes) **não estavam no formato exigido** por esta fase (frases de paciente, mapa sintoma→doença, frases rotuladas de risco), por isso todos os insumos acima foram **gerados novos** para a Fase 2. O corpus textual da Fase 1 foi usado apenas como referência de vocabulário clínico. Detalhes e fontes em [docs/fontes.md](docs/fontes.md).

**Riscos e limitações identificados:**
- Bases pequenas e simuladas (10 frases / 60 frases rotuladas): não substituem validação clínica real nem representam a diversidade de apresentação de sintomas na população.
- O matching por palavra-chave (Parte 1) e o TF-IDF (Parte 2) são sensíveis a vocabulário não visto em treino — na prática, isso pode gerar falsos negativos (sintoma grave não reconhecido) ou falsos positivos (alarme desnecessário), como demonstrado no erro discutido no notebook.
- Qualquer sistema real de triagem construído sobre esses princípios exigiria dataset muito maior, validação por profissionais de saúde e supervisão humana antes de qualquer uso assistencial.

---

## Critérios de Avaliação (10 pontos)

| Critério | Pontos | Entregável correspondente |
|---|---|---|
| Relatos e mapa de conhecimento organizados | 2 | `assets/frases_sintomas.txt`, `assets/mapa_conhecimento.csv` |
| Código de extração de informações funcional | 2 | `src/extracao_diagnostico.py` |
| Dataset simples criado corretamente | 1 | `assets/base_risco.csv` |
| Classificador treinado e testado corretamente | 2 | `notebooks/classificador_risco.ipynb` |
| Documentação clara e repositório público no GitHub com README completo | 1 | Este README + repositório |
| Vídeo de demonstração no YouTube (não listado) com link no GitHub | 2 | Ver seção abaixo |

---

## Vídeo de Demonstração

📺 [Link do vídeo no YouTube (não listado)] — *a incluir após a gravação*

---

## Como Executar

```bash
cd 2TIAO/FASE2
python3 src/extracao_diagnostico.py       # Parte 1
jupyter notebook notebooks/classificador_risco.ipynb   # Parte 2
```
