# Fontes de Dados e Literaturas de Referência - CardioIA

Este documento consolida a origem de todos os conjuntos de dados numéricos, temporais, visuais e textuais curados durante a Fase 1 para a construção dos módulos de Machine Learning, Visão Computacional, IoT e Processamento de Linguagem Natural.

## 1. Dados Numéricos (Cross-Sectional e Séries Temporais)
- **Dataset Clínico Principal:** Heart Disease Dataset. Disponibilizado no repositório UCI Machine Learning e espelhado via Kaggle.
  - *Uso:* Treinamento de classificadores para diagnóstico automatizado (Fase 2).
- **Séries Temporais (Simulação IoT):** Geração sintética via Python (`numpy` e `pandas`), desenvolvida pelo próprio grupo, modelada com base em perfis fisiológicos reais (crises hipertensivas e taquicardia) extraídos das diretrizes de cardiologia.
  - *Uso:* Treinamento do sistema preditivo de eventos cardíacos (Fase 6) e formatação de payload (Fase 3).

## 2. Dados Visuais (Imagens)
- **Dataset de Radiografias Torácicas:** Cardiomegaly Disease Prediction Dataset (Kaggle). Acervo contendo milhares de raios-X rotulados nas classes `false` (sem cardiomegalia) e `true` (com cardiomegalia).
  - *Uso:* Treinamento de algoritmos de Visão Computacional (CNNs) para reconhecimento de anomalias (Fase 4).
- **Dataset de ECG em Imagem:** "ECG Heart Categorization Dataset — Image Version" (Kaggle, mohamedeldakrory8),
  que combina duas bases biomédicas de referência:
    - MIT-BIH Arrhythmia Database (PhysioNet) — classes `N`, `S`, `V`, `F`, `Q`, conforme a taxonomia
      padrão AAMI EC57 de batimentos cardíacos.
    - PTB Diagnostic ECG Database (PhysioNet) — classes `N` (normal) e `M` (infarto do miocárdio).
  - *Uso:* Treinamento de CNNs para classificação multiclasse de arritmias e infarto a partir do
    traçado eletrocardiográfico (Fase 4).

## 3. Dados Textuais e Diretrizes (Corpus NLP)
A estruturação dos textos clínicos, documentos de orientação ao paciente e FAQs foi embasada nas seguintes diretrizes nacionais e internacionais (padrão-ouro em cardiologia):

*   **SBC (Sociedade Brasileira de Cardiologia):**
    *   Diretriz de Síndrome Coronariana Crônica - 2025. Arq Bras Cardiol. 2025; 122(9):e20250619.
    *   Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose - 2025. Arq Bras Cardiol. 2025; 122(9):e20250640.
    *   Diretriz Brasileira de Hipertensão Arterial - 2025. Arq Bras Cardiol. 2025; 122(9):e20250624.
*   **AHA/ACC (American Heart Association / American College of Cardiology):**
    *   2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the Management of Patients With Acute Coronary Syndromes. Circulation. 2025;151:e771–e862.
    *   2025 AHA/ACC/AANP/AAPA/ABC/ACCP/ACPM/AGS/AMA/ASPC/NMA/PCNA/SGIM Guideline for the Prevention, Detection, Evaluation and Management of High Blood Pressure in Adults. Hypertension. 2025;82:e212–e316.
    *   2026 ACC/AHA/AACVPR/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline on the Management of Dyslipidemia. Circulation. 2026;153:e1154–e1276.

  - *Uso:* Treinamento de Processamento de Linguagem Natural (NLP) e construção da base de conhecimento do assistente virtual (Fase 5).

Além das diretrizes científicas acima, o corpus inclui materiais de orientação ao paciente em
linguagem acessível e um FAQ estruturado, para garantir variedade de registro textual (científico
vs. leigo) e treinar o assistente virtual a se comunicar com o público geral:

*   **SBC — Diretrizes Clínicas para Leigos** (portal público de materiais educativos):
    *   Cartilha "Diretriz Brasileira de Hipertensão 2025 — o que é verdade (e o que não é)".
        Disponível em: https://www.portal.cardiol.br/diretrizes-clinicas-para-leigos
    *   Infográfico "O Cuidado Precoce Salva Vidas", produto da Diretriz Brasileira de Atendimento
        à Dor Torácica na Unidade de Emergência 2025. Disponível em:
        https://www.portal.cardiol.br/diretrizes-clinicas-para-leigos
    - *Uso:* Base para as cartilhas `cartilha-hipertensao-2025.txt` e
      `cartilha-dor-toracica-infarto.txt` (assets/textos/), representando o registro textual
      "cartilha de orientação ao paciente".
*   **Ministério da Saúde — Saúde de A a Z:** "Hipertensão (pressão alta)". Disponível em:
    https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/h/hipertensao
    - *Uso:* Base, junto com as fontes SBC acima, para o `faq-hipertensao-infarto.txt`
      (assets/textos/), reestruturado no formato Pergunta/Resposta pelo grupo.

### Nota de transparência — conteúdo gerado localmente

Os arquivos `guia-clinico-hipertensao.txt`, `faq-sintomas-e-cuidados-cardiologicos.txt`,
`cartilha-orientacao-diaria.txt` e `cartilha-orientacao-exames.txt` (assets/textos/) são
**conteúdo educativo elaborado pelo grupo para fins acadêmicos**, com base em conhecimento geral
de saúde cardiovascular de domínio público, e não foram extraídos de um documento oficial
específico e citável (cada arquivo traz sua própria nota de fonte/limitação no cabeçalho). Eles
complementam — sem duplicar — o material oficial (SBC/Ministério da Saúde) já referenciado acima,
ampliando a variedade de registros do corpus (guia técnico intermediário, FAQ mais amplo de
sintomas, cartilha de rotina diária e cartilha de exames) para treinamento do assistente virtual
(Fase 5). Não substituem diretrizes clínicas oficiais nem orientação médica individualizada.
