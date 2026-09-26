# Fontes e auditoria dos insumos da Fase 2

## 1. Decisão de geração de insumos novos

A Fase 2 do projeto CardioIA exige entradas em formatos específicos para a parte de extração de diagnóstico e para a parte de classificação de risco:

- frases em 1ª pessoa, em texto livre, para a Parte 1;
- mapa de conhecimento estruturado em CSV com sintoma e doença associada;
- base de risco rotulada em CSV com colunas `frase,situacao`.

Os arquivos produzidos na Fase 1 não atendem diretamente a esses requisitos. Em vez de reaproveitar dados brutos incompatíveis, o grupo decidiu usar o corpus textual da Fase 1 apenas como referência terminológica e clínica para a formulação de novos insumos, preservando coerência com o projeto e evitando retrabalho de pesquisa.

## 2. Auditoria de compatibilidade dos insumos da Fase 1

| Insumo da Fase 1 | Formato exigido pela Fase 2 | Compatível? | Observação |
|---|---|---|---|
| `dataset_cardiaco.csv` (`tipo_dor_peito` categórico/numérico) | Frases completas em 1ª pessoa descrevendo sintomas | ❌ Não | O dado é categórico e não textual; não serve como corpus de relato de paciente. |
| `assets/textos/*.txt` (13 diretrizes/cartilhas/FAQs) | Mapa sintoma → doença em CSV (`sintoma_1,sintoma_2,doenca_associada`) | ❌ Não | Os arquivos são textos corridos, não uma tabela estruturada de sintomas e doenças. |
| `assets/textos/*.txt` | Frases rotuladas `frase,situacao` (baixo/alto risco) | ❌ Não | Não há corpus de risco rotulado nem base de treino com labels. |

### Conclusão

A base da Fase 1 foi utilizada como referência de vocabulário clínico e de terminologia de sinais e sintomas, especialmente em materiais como:

- `faq-sintomas-e-cuidados-cardiologicos.txt`;
- `cartilha-dor-toracica-infarto.txt`;
- `faq-hipertensao-infarto.txt`.

Esses arquivos ajudam a manter consistência na linguagem dos novos insumos, mas não substituem a necessidade de criar um conjunto de dados novo e compatível com a Fase 2.

## 3. Fontes dos insumos novos

Os insumos novos da Fase 2 foram produzidos internamente pelo grupo, com base em:

- vocabulário clínico e sinais de alerta dos materiais da Fase 1;
- variações de linguagem em primeira pessoa para simular relatos de pacientes;
- combinação de sintomas e contextos para gerar um mapa de conhecimento e uma base de risco balanceada.

## 4. Observação sobre governança e uso de IA

Mesmo sendo um estudo acadêmico e simulado, o projeto reconhece que dados clínicos reais exigem cuidado. A estrutura adotada nesta fase é uma simplificação didática e não deve ser interpretada como ferramenta de decisão médica. O uso de palavras-chave e regras simples também tem limitações, especialmente em cenários de saúde, onde contextualização, viés de amostragem e falso negativo podem afetar resultados.

## 5. Insumos efetivamente gerados

| Arquivo | Conteúdo |
|---|---|
| `assets/frases_sintomas.txt` | 10 frases de pacientes, cobrindo 6 doenças (Infarto, Angina, Insuficiência Cardíaca, Arritmia, Hipertensão, AVC) |
| `assets/mapa_conhecimento.csv` | 32 linhas `sintoma_1,sintoma_2,doenca_associada` |
| `assets/base_risco.csv` | 60 frases rotuladas, balanceadas 30 alto risco / 30 baixo risco, incluindo ~13% de casos ambíguos propositais |
