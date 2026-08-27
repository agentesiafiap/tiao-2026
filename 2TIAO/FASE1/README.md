# CardioIA 🫀🤖

**Projeto:** Simulação de Ecossistema de Cardiologia Moderna com Inteligência Artificial
**Fase 1:** Batimentos de Dados – Mapeando o Coração Moderno

## 📌 Sobre o Projeto
As doenças cardiovasculares são a principal causa de mortes no mundo, com aproximadamente 17,9 milhões de óbitos anuais[cite: 2]. O projeto **CardioIA** visa criar uma plataforma digital interativa para revolucionar a cardiologia, antecipando eventos críticos e personalizando cuidados[cite: 2]. 

Nesta Fase 1, atuamos como cientistas de dados hospitalares com o objetivo de construir, organizar e documentar a base de dados (numéricos, textuais e visuais) que alimentará os futuros módulos de Machine Learning, IoT, Visão Computacional e Processamento de Linguagem Natural[cite: 2, 3].

---

## 📂 Estrutura dos Dados e Justificativas Técnicas

### Parte 1: Dados Numéricos (Cross-Sectional / IoT)
- **Fonte:** Heart Disease Dataset (Kaggle/UCI).
- **Volume:** 1025 registros estruturados.
- **Variáveis Principais:** `patient_id`, `idade`, `sexo`, `tipo_dor_peito`, `pressao_arterial_repouso`, `colesterol`, `freq_cardiaca_max`, `diagnostico` (target).
- **Justificativa Clínica e de IA:** Fornece um panorama transversal do risco cardiovascular. A seleção de variáveis (como pressão arterial e colesterol) permite a futura criação de hiperplanos de separação otimizados para algoritmos de Machine Learning (Fase 2)[cite: 2, 3].
- **Análise Exploratória (EDA):**
  - *Balanceamento:* O target (`diagnostico`) está equilibrado (51,3% positivo, 48,7% negativo), dispensando técnicas de sobreamostragem.
  - *Correlações:* O tipo de dor no peito e a frequência cardíaca máxima possuem forte correlação com desfechos positivos.
  - *Outliers:* Valores extremos biológicos foram identificados em variáveis como colesterol (máx: 564 mg/dl) e exigirão normalização escalar nas próximas etapas.

### Parte 1b: Dados Temporais (Séries Temporais)
- **Fonte:** Geração sintética (Python/NumPy) baseada em parâmetros clínicos.
- **Volume:** 125.000 eventos sequenciais de monitoramento (simulando 500 pacientes).
- **Variáveis Principais:** `patient_id`, `timestamp`, `frequencia_cardiaca`, `pressao_arterial_sistolica`, `evento`.
- **Justificativa Clínica e de IA:** Essencial para a Fase 6 (Previsão de Crises com IA)[cite: 2, 3]. Simula a telemetria contínua de sinais vitais, registrando o agravamento progressivo que antecede um evento crítico, fornecendo o substrato vetorial para treinamento de redes recorrentes (como LSTM).

### Parte 2: Dados Textuais (NLP)
O corpus de texto foi estruturado com 9 documentos em formato `.txt`, abrigados na pasta `assets/textos/`[cite: 3].
- **Conteúdo:**
  1. `diretriz-sbc-sindrome-coronariana-cronica-2025.txt` — Diretriz de Síndrome Coronariana Crônica (SBC).
  2. `diretriz-sbc-hipertensao-arterial-2025.txt` — Diretriz Brasileira de Hipertensão Arterial (SBC).
  3. `diretriz-sbc-dislipidemias-aterosclerose-2025.txt` — Diretriz de Dislipidemias e Prevenção da Aterosclerose (SBC).
  4. `diretriz-aha-acc-dislipidemia-2026.txt` — Guideline on the Management of Dyslipidemia (AHA/ACC).
  5. `diretriz-aha-acc-hipertensao-arterial-2025.txt` — Guideline for High Blood Pressure in Adults (AHA/ACC).
  6. `diretriz-aha-acc-sindrome-coronariana-aguda-2025.txt` — Guideline for Acute Coronary Syndromes (AHA/ACC).
  7. Cartilha de Orientação ao Paciente — Hipertensão 2025 (`cartilha-hipertensao-2025.txt`), versão em
     linguagem acessível ("mitos e fatos") da diretriz SBC de hipertensão, para o público leigo.
  8. Cartilha de Orientação ao Paciente — Sinais de Infarto (`cartilha-dor-toracica-infarto.txt`),
     infográfico da SBC sobre sinais de alerta de dor torácica/infarto.
  9. FAQ Estruturado (`faq-hipertensao-infarto.txt`), no formato `Pergunta: ... / Resposta: ...`,
     construído a partir de conteúdo oficial do Ministério da Saúde e da SBC.
- **Justificativa Clínica e de IA:** A vasta maioria do histórico do paciente reside em textos não estruturados. O arquivo de FAQ é a base direta exigida para o treinamento do assistente cardiológico virtual (chatbot) da Fase 5[cite: 2, 3]. As cartilhas, em linguagem acessível, treinam o modelo a se comunicar com o público leigo, enquanto as diretrizes científicas servem para Extração de Entidades Nomeadas (NER) e Análise de Sentimentos.

### Parte 3: Dados Visuais (Visão Computacional)
O acervo visual reúne dois tipos de exame cardiológico, organizados em `assets/imagens/{ECG,RX}/{train,test}/<classe>/`[cite: 3]:

- **Raio-X Torácico (`RX/`):**
  - **Fonte:** Cardiomegaly Disease Prediction (Kaggle).
  - **Classes:** `false` (sem cardiomegalia) e `true` (com cardiomegalia), conforme a rotulagem original do dataset.
  - **Volume:** > 5.000 imagens no acervo completo (hospedado no Drive); amostra local balanceada em `assets/imagens/RX/`.
  - **Justificativa Clínica e de IA:** O Raio-X permite avaliar a morfologia cardíaca (como o índice cardiotorácico para detecção de cardiomegalia). Em IA, essas matrizes de pixels servirão para treinar modelos de Redes Neurais Convolucionais (CNNs) na Fase 4, automatizando a detecção de anomalias[cite: 2, 3].
- **Eletrocardiograma em imagem (`ECG/`):**
  - **Fonte:** "ECG Heart Categorization Dataset — Image Version" (Kaggle), que combina o MIT-BIH Arrhythmia Database com o PTB Diagnostic ECG Database.
  - **Classes (taxonomia AAMI EC57 + PTB):** `N` (batimento normal), `S` (ectópico supraventricular), `V` (ectópico ventricular), `F` (fusão), `Q` (não classificável) — do MIT-BIH — e `M` (infarto do miocárdio) — do PTB Diagnostic ECG Database.
  - **Justificativa Clínica e de IA:** Permite treinar CNNs para classificação multiclasse de arritmias e infarto a partir da morfologia do traçado eletrocardiográfico, complementando o Raio-X com um exame de menor custo e uso mais frequente na triagem cardiológica.

---

## 🏛 Governança de Dados e Viés
A construção de soluções em saúde exige rigor técnico e ético[cite: 2, 3].
- **Privacidade:** Todos os datasets utilizados foram desidentificados e não contêm Informações Pessoais de Saúde (PHI) expostas.
- **Mitigação de Viés:** Reconhecemos que bases de dados históricas podem apresentar sub-representação de perfis patológicos atípicos (ex: sintomas de isquemia em mulheres). A diversidade do nosso corpus NLP e a amplitude das 5.000 imagens visam reduzir a propagação de viés discriminatório nos futuros algoritmos.

---

## 🔗 Acesso aos Arquivos e Datasets Completos
Os conjuntos de dados (Numéricos, Temporais e Visuais), organizados conforme a arquitetura proposta, excedem os limites de armazenamento padrão e estão hospedados publicamente no link abaixo:

**👉 [https://drive.google.com/drive/folders/1MjRjubKeXP5wfsZqoUAp35yOG_cBH_st?usp=share_link](https://drive.google.com/drive/folders/1MjRjubKeXP5wfsZqoUAp35yOG_cBH_st?usp=share_link) 👈**

*(Aviso: O link está configurado como público para garantir o acesso da banca avaliadora da FIAP[cite: 3]).*

---
## 👥 Grupo 78 - Integrantes
- Hugo Rodrigues
- Daniel Emilio Baião
