# Plano de Implementação – CardioIA: Fase 1 – Batimentos de Dados

**Curso:** IA – 2º TIAO  
**Atividade:** Cap 1 – A Busca de Dados: Preparando o Terreno para a Inteligência Cardiológica  
**Grupo:** 37  
**Prazo de entrega:** Quarta-feira, 02 de setembro de 2026, às 23h59  

---

## Contexto

O **CardioIA** é um projeto acadêmico PBL que simula o ecossistema de uma cardiologia moderna, integrando IoT, NLP e Visão Computacional. A **Fase 1** tem como objetivo levantar, organizar e documentar dados cardiológicos que servirão de base para os módulos inteligentes das fases seguintes.

O grupo assume o papel de **cientista de dados hospitalar** e deve coletar três tipos de dados fundamentais:

| Tipo | Parte | Técnica Futura | Fases Dependentes |
|------|-------|----------------|-------------------|
| Numérico (cross-sectional) | Parte 1 | ML supervisionado | Fase 2 |
| Numérico (séries temporais) | Parte 1b | Predição temporal | Fase 6 |
| Textual | Parte 2 | NLP / Chatbot | Fase 5 |
| Visual | Parte 3 | Visão Computacional | Fase 4 |

> ⚠️ **Nota de arquitetura:** A Fase 1 é a única oportunidade de definir a fundação de dados para todo o projeto. Decisões tomadas aqui (esquema de variáveis, padrão de identificação de pacientes, volume e qualidade dos dados) impactam diretamente todas as fases seguintes.

---

## Estrutura do Repositório

```
cardio-ia-fase1/
├── README.md                    ← Documento principal (entregável obrigatório)
├── assets/
│   ├── dados_numericos/         ← CSV/XLSX do dataset de pacientes (cross-sectional)
│   ├── dados_temporais/         ← CSV/XLSX ou referência ao dataset de séries temporais
│   ├── textos/                  ← Arquivos .txt dos textos médicos
│   └── imagens/                 ← (link externo; pasta local de referência)
├── notebooks/                   ← Pasta para notebooks futuros (Colab/Jupyter)
└── docs/
    ├── fontes.md                ← Referências e links das fontes utilizadas
    ├── data_dictionary.md       ← Dicionário de variáveis com tipos e descrições
    └── iot_schema.json          ← Schema do payload IoT para a Fase 3
```

> As imagens e o dataset completo devem ser hospedados no **Google Drive ou OneDrive** com link público. O repositório no GitHub deve conter o link no README.md.

---

## Parte 1 – Dados Numéricos (IoT)

### Objetivo
Buscar e organizar um dataset com **mínimo 100 linhas** contendo variáveis clínicas cardiológicas.

### Variáveis-alvo sugeridas
- `patient_id` – identificador único do paciente (**obrigatório**; será reutilizado em todas as fases)
- `idade` – fator de risco crescente com o envelhecimento
- `sexo` – distribuição diferencial de doenças cardiovasculares
- `pressao_arterial` – principal indicador de risco cardíaco
- `colesterol` – marcador lipídico diretamente associado a doenças coronarianas
- `frequencia_cardiaca` – variável monitorada por dispositivos IoT
- `historico_doencas` – flag binário ou categórico de condições pré-existentes
- `sintomas` – dor no peito, falta de ar, palpitações, etc.
- `diagnostico` – target (presença ou ausência de doença cardíaca)

### Fontes sugeridas
- [UCI Heart Disease Dataset](https://archive.ics.uci.edu/ml/datasets/heart+disease) – dataset real amplamente utilizado
- [Kaggle – Heart Disease](https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset) – versão pré-processada
- Geração sintética com bibliotecas como `Faker` ou `numpy.random` (caso uso real seja inviável)

> ⚠️ **Atenção (FIAP):** buscar datasets públicos na internet é uma das tarefas mais desafiadoras para qualquer profissional de IA, especialmente quando o tema envolve áreas sensíveis como saúde, finanças, educação e dados pessoais. Muitos desses dados são protegidos por questões éticas, legais e de privacidade, tornando sua disponibilização pública extremamente restrita. Mesmo quando os dados existem, é normal que estejam espalhados em repositórios pouco conhecidos, em formatos desorganizados ou exijam processos de autorização para acesso.

### Passos de implementação
1. Selecionar ou gerar o dataset
2. Adicionar coluna `patient_id` (formato `PAC-0001`, `PAC-0002`, …)
3. Verificar integridade: checar valores nulos, tipos de colunas, distribuição de classes
4. Realizar EDA mínima e documentar no README:
   - Distribuição da variável `diagnostico` (balanceamento de classes)
   - Correlações entre variáveis e o target
   - Outliers relevantes e estratégia de tratamento
5. Salvar como `assets/dados_numericos/dataset_cardiaco.csv`
6. Hospedar cópia completa no Google Drive/OneDrive com link público
7. Redigir seção no README.md com:
   - Origem dos dados (real ou simulado)
   - Descrição das variáveis
   - Justificativa clínica das variáveis mais relevantes
   - Link para os dados hospedados

### Formato de entrega
- `assets/dados_numericos/dataset_cardiaco.csv` **ou** `dataset_cardiaco.xlsx` (ou amostra)
- Seção "Parte 1" no `README.md` com EDA mínima documentada

---

## Parte 1b – Dados Temporais (Séries Temporais)

> ⚠️ **Necessário para a Fase 6.** A Fase 6 exige dados sequenciais com timestamps. O dataset cross-sectional da Parte 1 não é suficiente para treinar modelos de predição temporal.

### Objetivo
Levantar um dataset com **medições repetidas ao longo do tempo** do mesmo paciente, viabilizando a Fase 6 (Previsão de Crises com IA).

### Fontes sugeridas
- [MIT-BIH Arrhythmia Database (PhysioNet)](https://physionet.org/content/mitdb/1.0.0/) – sinais de ECG contínuos rotulados
- [PTB-XL ECG Dataset (PhysioNet)](https://physionet.org/content/ptb-xl/1.0.3/) – 21.799 ECGs de 12 derivações com rótulos clínicos
- [MIMIC-III Waveforms](https://physionet.org/content/mimic3wdb/1.0/) – sinais vitais contínuos de UTI (requer credencial gratuita PhysioNet)
- Geração sintética de séries temporais com `numpy` ou `tsfresh` caso as fontes acima sejam inviáveis

### Variáveis mínimas esperadas
- `patient_id` – mesmo identificador da Parte 1
- `timestamp` – data/hora da medição
- `frequencia_cardiaca` – valor medido no instante
- `pressao_arterial` – valor medido no instante
- `evento` – flag binário indicando ocorrência de evento crítico (arritmia, crise, etc.)

### Passos de implementação
1. Selecionar a fonte e baixar uma amostra representativa
2. Padronizar colunas conforme variáveis mínimas acima
3. Salvar como `assets/dados_temporais/dataset_temporal.csv`
4. Hospedar conjunto completo no Google Drive/OneDrive com link público
5. Documentar no README: fonte, frequência de amostragem, número de pacientes e eventos

### Formato de entrega
- `assets/dados_temporais/dataset_temporal.csv` **ou** `dataset_temporal.xlsx` (ou amostra)
- Seção "Parte 1b" no `README.md`

---

## Parte 2 – Dados Textuais (NLP)

### Objetivo
Baixar **mínimo 5 arquivos .txt** com textos relacionados a doenças cardíacas, saúde cardiovascular, sintomas ou tratamentos.

> ⚠️ **Necessário para a Fase 5.** O chatbot da Fase 5 precisará de um corpus estruturado de sintomas, orientações e FAQs. Dois textos genéricos não são suficientes para construir uma base de conhecimento funcional.

### Fontes sugeridas
- [SciELO](https://www.scielo.br) – artigos científicos em português/espanhol
- [BVS – Biblioteca Virtual em Saúde](https://bvsalud.org) – literatura técnica e de saúde pública
- [Ministério da Saúde / SUS](https://www.gov.br/saude) – guias e manuais clínicos
- [Projeto Gutenberg](https://www.gutenberg.org) – literatura clássica (para análise de linguagem)

### Critérios de seleção
- Relevância temática: cardiologia, prevenção cardiovascular, hábitos saudáveis
- Tamanho mínimo: textos com paragrafação suficiente para análise de NLP
- Variedade obrigatória:
  - ≥ 1 artigo científico ou técnico (SciELO, BVS)
  - ≥ 1 guia ou manual clínico do Ministério da Saúde
  - ≥ 1 documento em formato FAQ ou perguntas e respostas sobre sintomas cardíacos (**base direta para o chatbot da Fase 5**)
  - ≥ 2 textos de orientação ao paciente (linguagem acessível)

### Possibilidades de exploração por NLP (justificativa)
- **Análise de sentimentos:** identificar tom positivo/negativo em relatos de pacientes
- **Extração de entidades:** detectar nomes de medicamentos, sintomas e condições
- **Classificação de tópicos:** agrupar textos por tema (prevenção, diagnóstico, tratamento)
- **Sumarização automática:** gerar resumos de artigos científicos para uso clínico

### Passos de implementação
1. Selecionar e baixar os textos (mínimo 5)
2. Salvar como `.txt` em `assets/textos/texto_01.txt`, `texto_02.txt`, etc.
3. Garantir encoding UTF-8 sem erros de caracteres especiais
4. Para o documento FAQ: estruturar em pares `Pergunta: ... / Resposta: ...` para facilitar ingestão no chatbot da Fase 5
5. Redigir seção no README.md com:
   - Título e fonte de cada texto
   - Tipo de cada texto (científico / guia clínico / FAQ / orientação ao paciente)
   - Como cada texto pode ser explorado por NLP
   - Justificativa da relevância para IA em saúde

### Formato de entrega
- `assets/textos/texto_01.txt` até `texto_05.txt` (mínimo)
- Seção "Parte 2" no `README.md`

---

## Parte 3 – Dados Visuais (Visão Computacional)

### Objetivo
Reunir **mínimo 500 imagens rotuladas** (.jpg ou .png) de um tipo de exame cardiológico, organizadas em no mínimo 2 classes balanceadas.

> ⚠️ **Necessário para a Fase 4.** 100 imagens sem rótulos definidos são insuficientes para treinar qualquer modelo de classificação — mesmo com Transfer Learning. Rótulos são obrigatórios e o balanceamento de classes deve ser verificado.

### Tipos de exame sugeridos (escolher um)
| Exame | Descrição | Aplicação em VC |
|-------|-----------|-----------------|
| **ECG** | Eletrocardiograma digitalizado | Detecção de arritmias por padrão de onda |
| **Raio-X torácico** | Imagem de tórax | Identificação de cardiomegalia, derrames |
| **Angiograma coronário** | Imagem de vascularização | Detecção de obstruções e estenoses |

### Fontes sugeridas
- [PhysioNet](https://physionet.org) – base de dados biomédicos aberta
- [Kaggle – Chest X-Ray Images](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia) – raios-X rotulados
- [NIH Chest X-rays](https://www.kaggle.com/datasets/nih-chest-xrays/data) – 100k+ imagens
- [ECG Image Dataset](https://www.kaggle.com/datasets/shayanfazeli/heartbeat) – sinais de ECG como imagens

### Possibilidades de exploração por Visão Computacional (justificativa)
- **Detecção de padrões:** identificar morfologia de ondas P, QRS, T em ECGs
- **Identificação de bordas:** segmentar estruturas cardíacas em raios-X
- **Reconhecimento de anomalias:** classificar exames normais vs. patológicos
- **Transfer Learning:** fine-tuning de modelos como ResNet ou EfficientNet para diagnóstico

### Passos de implementação
1. Selecionar a fonte e o tipo de exame — **priorizar datasets já rotulados** (Kaggle Chest X-Ray, PTB-XL)
2. Verificar e documentar o balanceamento de classes (ex: `NORMAL` vs. `PATOLÓGICO`)
3. Baixar e organizar as imagens em subpastas obrigatórias por classe: `assets/imagens/normal/` e `assets/imagens/patologico/`
4. Verificar resolução mínima das imagens (recomendado ≥ 128×128 px)
5. Hospedar o conjunto completo no Google Drive/OneDrive com link público
6. Criar pasta local de referência em `assets/imagens/` (pode conter apenas amostras)
7. Redigir seção no README.md com:
   - Tipo de exame escolhido e fonte
   - Número total de imagens por classe
   - Resolução das imagens
   - Link público para o acervo completo
   - Justificativa das aplicações em Visão Computacional

### Formato de entrega
- Link público (Google Drive/OneDrive) com as 500+ imagens organizadas por classe
- Seção "Parte 3" no `README.md`

---

## Fundação para Fases Futuras

Esta seção define artefatos que **não são entregáveis avaliados na Fase 1**, mas que devem ser produzidos para evitar retrabalho nas fases seguintes.

### Dicionário de Dados (`docs/data_dictionary.md`)

Documentar todas as variáveis coletadas nas Partes 1, 1b, 2 e 3 em um único arquivo de referência:

```markdown
| Variável          | Tipo     | Parte | Descrição                          | Fases que usam |
|-------------------|----------|-------|------------------------------------|----------------|
| patient_id        | string   | 1, 1b | Identificador único do paciente    | 2, 3, 4, 5, 6, 7 |
| frequencia_cardiaca | float  | 1, 1b | Batimentos por minuto              | 2, 3, 6 |
| diagnostico       | int(0/1) | 1     | Target: presença de doença cardíaca | 2 |
| timestamp         | datetime | 1b    | Instante da medição                | 6 |
| evento            | int(0/1) | 1b    | Ocorrência de evento crítico       | 6 |
| ...               | ...      | ...   | ...                                | ... |
```

### Schema IoT (`docs/iot_schema.json`)

Definir o formato do payload que o wearable simulado (ESP32) da Fase 3 deverá emitir, com base nas variáveis coletadas na Fase 1:

```json
{
  "patient_id": "PAC-0001",
  "timestamp": "2026-09-01T10:30:00Z",
  "frequencia_cardiaca": 78,
  "pressao_arterial_sistolica": 120,
  "pressao_arterial_diastolica": 80,
  "temperatura_corporal": 36.7,
  "spo2": 98
}
```

> Este schema deve ser entregue junto com o repositório para que a Fase 3 possa ser implementada sem ambiguidade.

---

## README.md – Estrutura Sugerida

```markdown
# CardioIA – Fase 1: Batimentos de Dados

## Sobre o Projeto
[Contextualização do CardioIA e objetivo da Fase 1]

## Parte 1 – Dados Numéricos (IoT)
- Fonte: [...]
- Variáveis: [...]
- Relevância clínica: [...]
- Link para os dados: [Google Drive/OneDrive]

## Parte 1b – Dados Temporais
- Fonte: [...]
- Variáveis: patient_id, timestamp, frequencia_cardiaca, pressao_arterial, evento
- Link para os dados: [Google Drive/OneDrive]

## Parte 2 – Dados Textuais (NLP)
- Texto 1: Título, fonte, tipo (científico / guia / FAQ / orientação), potencial de exploração
- Texto 2: Título, fonte, tipo, potencial de exploração
- Texto 3–5: [...]
- Justificativa para NLP em saúde: [...]

## Parte 3 – Dados Visuais (Visão Computacional)
- Tipo de exame: [ECG / Raio-X / Angiograma]
- Fonte: [...]
- Total de imagens por classe: [normal: X | patológico: Y]
- Resolução: [...]
- Link para as imagens: [Google Drive/OneDrive]
- Aplicações em VC: [...]

## Governança de Dados e Viés
[Considerações sobre origem dos dados, privacidade, possíveis vieses]

## Integrantes do Grupo 37
- [Nome – RM]
```

---

## Checklist Final de Entrega

**Entregáveis obrigatórios (avaliados):**
- [ ] Repositório público no GitHub criado
- [ ] `README.md` completo com as seções de Parte 1, 2 e 3
- [ ] `assets/dados_numericos/dataset_cardiaco.csv` presente com coluna `patient_id`
- [ ] EDA mínima documentada no README (distribuição de classes, correlações, outliers)
- [ ] `assets/textos/` com mínimo 5 arquivos .txt (incluindo 1 FAQ estruturado)
- [ ] `assets/imagens/normal/` e `assets/imagens/patologico/` com ≥ 500 imagens no total
- [ ] `docs/fontes.md` com referências de todas as fontes
- [ ] Dataset numérico hospedado com link público no README
- [ ] 500+ imagens hospedadas e organizadas por classe, com link público no README
- [ ] **Verificar acessibilidade de todos os links públicos** (Google Drive/OneDrive abertos para "qualquer pessoa com o link" — exigência da correção FIAP)
- [ ] Pasta `notebooks/` criada no repositório (mesmo vazia)
- [ ] Link do repositório GitHub submetido na plataforma FIAP antes de **02/09/2026 às 23h59**

**Artefatos de fundação para fases seguintes (não avaliados na Fase 1, mas obrigatórios para continuidade):**
- [ ] `assets/dados_temporais/dataset_temporal.csv` com variáveis temporais para a Fase 6
- [ ] `docs/data_dictionary.md` com todas as variáveis e as fases que as consomem
- [ ] `docs/iot_schema.json` com o schema do payload IoT para a Fase 3

---

## Observações sobre Governança de Dados

- **Dados reais de pacientes:** nunca utilizar dados identificáveis sem anonimização
- **Licenciamento:** verificar se os datasets permitem uso acadêmico (Creative Commons, MIT, etc.)
- **Viés:** documentar possíveis vieses nos dados (ex.: sub-representação de grupos étnicos, desbalanceamento de classes)
- **Rastreabilidade:** registrar exatamente de onde cada dado foi obtido para reprodutibilidade
