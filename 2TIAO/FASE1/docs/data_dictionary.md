# Dicionário de Dados – CardioIA (Fase 1)

Documento de referência com todas as variáveis coletadas nas Partes 1, 1b, 2 e 3, e as fases do projeto que as consomem.

| Variável | Tipo | Parte | Descrição | Fases que usam |
|---|---|---|---|---|
| patient_id | string | 1, 1b | Identificador único do paciente (formato `PAC-0001`) | 2, 3, 4, 5, 6, 7 |
| idade | int | 1 | Idade do paciente em anos | 2 |
| sexo | int (0/1) | 1 | Sexo biológico do paciente | 2 |
| tipo_dor_peito | int (categórico) | 1 | Classificação clínica do tipo de dor torácica | 2 |
| pressao_arterial_repouso | int | 1 | Pressão arterial sistólica em repouso (mmHg) | 2 |
| colesterol | int | 1 | Colesterol sérico (mg/dl) | 2 |
| glicemia_jejum | int (0/1) | 1 | Glicemia de jejum > 120 mg/dl | 2 |
| ecg_repouso | int (categórico) | 1 | Resultado do eletrocardiograma em repouso | 2 |
| freq_cardiaca_max | int | 1 | Frequência cardíaca máxima atingida | 2 |
| angina_exercicio | int (0/1) | 1 | Presença de angina induzida por exercício | 2 |
| depressao_st | float | 1 | Depressão do segmento ST induzida por exercício | 2 |
| inclinacao_st | int (categórico) | 1 | Inclinação do segmento ST no pico do exercício | 2 |
| vasos_coloridos_fluorscopia | int | 1 | Número de vasos principais coloridos por fluoroscopia | 2 |
| talassemia | int (categórico) | 1 | Resultado do exame de talassemia | 2 |
| diagnostico | int (0/1) | 1 | Target: presença de doença cardíaca | 2 |
| timestamp | datetime | 1b | Instante da medição (ISO 8601) | 6 |
| frequencia_cardiaca | int | 1, 1b | Batimentos por minuto medidos no instante | 2, 3, 6 |
| pressao_arterial_sistolica | int | 1b | Pressão arterial sistólica medida no instante (mmHg) | 3, 6 |
| pressao_arterial_diastolica | int | 1b | Pressão arterial diastólica medida no instante (mmHg) | 3, 6 |
| evento | int (0/1) | 1b | Ocorrência de evento crítico (arritmia, crise, etc.) | 6 |
| texto (corpus) | texto livre / estruturado | 2 | Diretrizes científicas, cartilhas de orientação ao paciente e FAQ estruturado (`Pergunta:`/`Resposta:`) | 5 |
| imagem (raio-X) | binário (png) | 3 | Radiografia torácica (`assets/imagens/RX/`) rotulada como `false` (sem cardiomegalia) ou `true` (com cardiomegalia) | 4 |
| imagem (ECG) | binário (png) | 3 | Eletrocardiograma em imagem (`assets/imagens/ECG/`), rotulado em 6 classes: `N` (normal), `S` (ectópico supraventricular), `V` (ectópico ventricular), `F` (fusão), `Q` (não classificável) — MIT-BIH — e `M` (infarto do miocárdio) — PTB Diagnostic ECG Database | 4 |
