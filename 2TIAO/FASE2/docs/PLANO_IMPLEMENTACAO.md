# Plano de Implementação – CardioIA: Fase 2 – Diagnóstico Automatizado

**Curso:** IA – 2º TIAO
**Atividade:** Cap 2 – Diagnóstico Automatizado: IA no Estetoscópio Digital
**Grupo:** 78

---

## Contexto

A **Fase 2** do CardioIA propõe simular a automatização do diagnóstico clínico com IA, trabalhando com **extração de informações em texto**, **classificação de risco (NLP + ML)** e uma primeira reflexão sobre **viés em dados de saúde**. O enunciado sugere reaproveitar o dataset da Fase 1, mas permite (e aqui se justifica) a criação de insumos novos quando os existentes não atendem ao formato exigido.

---

## Auditoria dos Insumos da Fase 1

| Insumo da Fase 1 | Formato exigido pela Fase 2 | Compatível? |
|---|---|---|
| `dataset_cardiaco.csv` (`tipo_dor_peito` categórico/numérico) | Frases completas em 1ª pessoa descrevendo sintomas | ❌ Não — é um código categórico, não texto livre |
| `assets/textos/*.txt` (13 diretrizes/cartilhas/FAQs) | Mapa sintoma → doença em `.csv` (Sintoma 1 \| Sintoma 2 \| Doença) | ❌ Não — é texto corrido, não uma tabela estruturada |
| `assets/textos/*.txt` | Frases rotuladas `frase,situacao` (baixo/alto risco) | ❌ Não existe rotulação de risco no corpus da Fase 1 |

**Conclusão:** os insumos da Fase 1 **não são reaproveitáveis diretamente** — nenhum arquivo está no formato de entregável exigido pela Fase 2. Serão **gerados insumos novos**, usando o corpus textual da Fase 1 como **referência de vocabulário clínico e de doenças** (principalmente `faq-sintomas-e-cuidados-cardiologicos.txt`, `cartilha-dor-toracica-infarto.txt` e `faq-hipertensao-infarto.txt`), garantindo coerência terminológica com o projeto e evitando retrabalho de pesquisa. Essa reutilização (como referência, não como dado bruto) deve ser registrada em `docs/fontes.md` da Fase 2.

---

## Decisões de Implementação

| Decisão | Escolha |
|---|---|
| Repositório | Mesmo monorepo do projeto (`tiao-2026`), pasta `2TIAO/FASE2/` — sem repositório dedicado |
| Código da Parte 1 | Script `.py` (`src/extracao_diagnostico.py`) |
| Classificador da Parte 2 | Treinar **Logistic Regression** e **Decision Tree**, comparar acurácia e escolher o melhor |
| Volume dos insumos novos | Reforçado: mapa de conhecimento com ~30 linhas; base de risco rotulada com ~40–60 frases balanceadas |

---

## Estrutura do Repositório (a criar)

```
2TIAO/FASE2/
├── README.md                       ← Documento principal (entregável obrigatório)
├── assets/
│   ├── frases_sintomas.txt         ← Parte 1: 10 frases de sintomas de pacientes
│   ├── mapa_conhecimento.csv       ← Parte 1: sintoma_1, sintoma_2, doenca_associada (~30 linhas)
│   └── base_risco.csv              ← Parte 2: frase, situacao (baixo risco / alto risco) (~40-60 linhas)
├── src/
│   └── extracao_diagnostico.py     ← Parte 1: leitura das frases, matching de sintomas, sugestão de diagnóstico
├── notebooks/
│   └── classificador_risco.ipynb   ← Parte 2: TF-IDF + treino/avaliação dos classificadores
└── docs/
    ├── PLANO_IMPLEMENTACAO.md      ← Este documento
    └── fontes.md                   ← Proveniência dos insumos novos e nota de reaproveitamento da Fase 1
```

---

## Fase 0 – Setup & Auditoria

### Objetivo
Criar a estrutura de pastas da Fase 2 e formalizar a auditoria de compatibilidade dos insumos da Fase 1 (ver seção acima).

### Passos
1. Criar as pastas `assets/`, `src/`, `notebooks/`, `docs/` em `2TIAO/FASE2/`.
2. Registrar em `docs/fontes.md` a decisão de gerar insumos novos e a justificativa (tabela de auditoria acima).

### Entregável
- Estrutura de pastas criada (sem entregáveis avaliativos nesta fase).

---

## Fase 1 – Parte 1: Insumos (Frases e Mapa de Conhecimento)

*Depende da Fase 0.*

### Objetivo
Produzir os dois insumos textuais/estruturados exigidos pela Parte 1 do enunciado.

### `assets/frases_sintomas.txt`
- 10 frases completas, variadas, em 1ª pessoa, simulando relatos de pacientes distintos.
- Cada frase deve conter: sintoma, tempo de início e impacto na rotina (ex.: *"Há dois dias estou com uma dor no peito que piora quando faço esforço físico"*).
- Cobrir múltiplas doenças-alvo (Infarto, Angina, Insuficiência Cardíaca, Arritmia, Hipertensão, AVC), evitando que todas as frases apontem para o mesmo diagnóstico.
- Vocabulário grounded no corpus da Fase 1 (FAQs e cartilhas de sintomas/sinais de alerta).

### `assets/mapa_conhecimento.csv`
- Colunas: `sintoma_1, sintoma_2, doenca_associada`.
- ~30 linhas, cobrindo as doenças usadas nas 10 frases acima e sinônimos/variações de cada sintoma (ex.: "dor no peito", "aperto no tórax", "dor torácica" → Infarto).
- Construído a partir dos sintomas e sinais de alerta descritos nas diretrizes/cartilhas/FAQs da Fase 1.

### Entregáveis
- `assets/frases_sintomas.txt`
- `assets/mapa_conhecimento.csv`

---

## Fase 2 – Parte 1: Código de Extração e Diagnóstico

*Depende da Fase 1.*

### Objetivo
Implementar `src/extracao_diagnostico.py`, que lê as frases, identifica sintomas via o mapa de conhecimento e sugere um diagnóstico.

### Passos
1. Carregar `frases_sintomas.txt` e `mapa_conhecimento.csv`.
2. Normalizar texto (minúsculas, remoção de acentos/pontuação) para tornar o matching robusto.
3. Para cada frase, buscar ocorrência de cada sintoma do mapa (busca por substring/expressão) e listar os sintomas identificados.
4. Agregar os sintomas encontrados para sugerir a doença mais provável (contagem de matches por doença); tratar o caso de nenhum sintoma identificado e o caso de empate/múltiplas doenças candidatas.
5. Imprimir/exportar uma tabela: `frase | sintomas_identificados | diagnostico_sugerido`.

### Entregável
- `src/extracao_diagnostico.py` funcional, executável via `python src/extracao_diagnostico.py`.

---

## Fase 3 – Parte 2: Insumos (Base de Risco Rotulada)

*Pode ser produzida em paralelo às Fases 1–2, mas será sequenciada nesta ordem de execução.*

### Objetivo
Criar `assets/base_risco.csv` para treinar o classificador de risco.

### Passos
1. Criar colunas `frase, situacao` (`situacao` ∈ {"baixo risco", "alto risco"}).
2. Redigir ~40–60 frases balanceadas entre as duas classes, com vocabulário parcialmente distinto do `mapa_conhecimento.csv` (para evitar que o classificador aprenda apenas keyword-matching trivial e force o uso real do TF-IDF).
3. Incluir variações de intensidade e contexto (ex.: dor leve vs. dor intensa e súbita) para dar sinal ao modelo.

### Entregável
- `assets/base_risco.csv`

---

## Fase 4 – Parte 2: Notebook de Classificação

*Depende da Fase 3.*

### Objetivo
Implementar `notebooks/classificador_risco.ipynb` com o pipeline de classificação de risco.

### Passos
1. Carregar `base_risco.csv`; conferir balanceamento das classes.
2. Dividir em treino/teste (`train_test_split`, com estratificação).
3. Vetorizar as frases com `TfidfVectorizer`.
4. Treinar dois modelos: `LogisticRegression` e `DecisionTreeClassifier`.
5. Avaliar ambos (acurácia, matriz de confusão, precisão/recall) e escolher o melhor.
6. Testar o modelo escolhido com frases novas (fora da base de treino) e comentar padrões/distorções observados (ex.: viés para termos específicos, poucos dados).

### Entregável
- `notebooks/classificador_risco.ipynb` executado, com outputs de métricas visíveis.

---

## Fase 5 – Documentação e Governança

*Depende das Fases 2 e 4.*

### Objetivo
Consolidar a documentação exigida e a reflexão sobre governança/viés em IA na saúde.

### Passos
1. Redigir `README.md` da Fase 2 com: contexto, Parte 1 (frases + mapa + código), Parte 2 (base de risco + notebook + métricas), tabela de critérios de avaliação, instruções de execução, integrantes do grupo.
2. Redigir `docs/fontes.md` com a proveniência dos insumos novos e a nota de reaproveitamento do corpus da Fase 1 (auditoria da Fase 0).
3. Incluir seção de reflexão sobre viés/governança: tamanho reduzido e caráter simulado da base, risco de falso negativo em triagem clínica real, limitações do matching por palavra-chave.

### Entregável
- `README.md` e `docs/fontes.md` completos.

---

## Fase 6 – Vídeo e Entrega Final

*Depende da Fase 5.*

### Objetivo
Produzir o vídeo de demonstração e fechar a submissão.

### Passos
1. Gravar vídeo de até 4 minutos demonstrando a Parte 1 (extração/diagnóstico) e a Parte 2 (classificador de risco).
2. Publicar no YouTube como "não listado".
3. Incluir o link do vídeo no `README.md`.
4. Conferir o checklist final abaixo e submeter o link do repositório na plataforma FIAP.

---

## Checklist Final de Entrega

- [ ] `assets/frases_sintomas.txt` com 10 frases variadas
- [ ] `assets/mapa_conhecimento.csv` com o mapa sintoma → doença
- [ ] `src/extracao_diagnostico.py` funcional, lendo as frases e sugerindo diagnósticos
- [ ] `assets/base_risco.csv` com frases rotuladas (baixo risco / alto risco)
- [ ] `notebooks/classificador_risco.ipynb` com TF-IDF, treino, comparação de modelos e avaliação
- [ ] `README.md` completo com todas as seções e tabela de critérios
- [ ] `docs/fontes.md` com a auditoria dos insumos da Fase 1 e proveniência dos novos insumos
- [ ] Repositório público no GitHub (monorepo `tiao-2026`) atualizado
- [ ] Vídeo de até 4 minutos no YouTube (não listado), com link no README
- [ ] Link do repositório enviado na plataforma FIAP dentro do prazo

---

## Fora de Escopo (não implementar nesta fase)

- **Ir Além 1** – Interface do CardioIA em React + Vite.
- **Ir Além 2** – Rede neural MLP para classificação de imagens de ECG.