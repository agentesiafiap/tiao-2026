# Notas herdadas da Fase 1 — pontos a tratar na Fase 4

Origem: feedback do professor sobre a entrega da Fase 1 (nota 17.5/18), ver
`2TIAO/FASE1/docs/avaliacao_do_professor.md` e o adendo em `2TIAO/FASE1/README.md`.

Itens relevantes para o treinamento dos classificadores de imagem (ECG/RX) nesta fase:

- **Split treino/validação/teste por paciente/exame**, não por imagem isolada. Exames ou
  batimentos do mesmo paciente/registro original (ex.: mesmo traçado MIT-BIH/PTB, mesmo
  paciente do dataset de cardiomegalia) devem permanecer no mesmo conjunto, para evitar
  vazamento de informação entre treino e teste.
- **Manifesto do acervo visual**: antes de treinar, gerar um arquivo (csv/json) com
  nome do arquivo, classe, origem (dataset) e identificador do paciente/exame quando
  disponível, cobrindo o acervo completo hospedado no Drive (não só as ~230 amostras
  locais da Fase 1).
- **Desbalanceamento do ECG**: predomínio da classe `N` (~94.675 de 124.087 imagens).
  Definir e aplicar estratégia de balanceamento (undersampling, oversampling, pesos de
  classe ou focal loss) e monitorar recall por classe minoritária (`F`, `S`, `V`, `Q`, `M`),
  não apenas acurácia global — risco de viés diagnóstico já documentado na Fase 1.
- **Escolher uma única modalidade por experimento** (RX ou ECG), evitando dispersão entre
  os dois tipos de exame na mesma rodada de treinamento/avaliação.
- **Limitações demográficas/geográficas das fontes** (UCI, MIT-BIH, PTB, datasets do
  Kaggle): documentar possíveis vieses de representatividade antes de generalizar
  conclusões do modelo.
- **Reprodutibilidade da base temporal sintética**: o script que gerou
  `assets/dados_temporais/dataset_temporal.csv` (125k eventos) ainda não foi recuperado/
  versionado. Se for reaproveitado na Fase 6, buscar ou recriar esse script e documentar
  as regras clínicas usadas (crises hipertensivas, taquicardia etc.).
