Na **Fase 1 – Batimentos de Dados**, você assume o papel de **cientista de dados hospitalar:** seu desafio é levantar, organizar e entender dados cardiológicos que, futuramente, alimentarão os módulos inteligentes do CardioIA. Aqui você constrói a base! E o mais importante, de olho na Governança de Dados envolvendo IA.
 
**Objetivo geral da atividade:**
Você deverá buscar e preparar **três tipos de dados fundamentais:**
- **Dados numéricos (simulados ou reais) relacionados a pacientes cardíacos;**
- **Textos médicos ou literários relacionados à saúde cardiovascular;**
- **Imagens médicas que representem exames ou sinais visuais do coração.**

Esses dados serão utilizados nas fases seguintes do projeto para alimentar algoritmos, treinar modelos de IA, fazer análises comparativas e gerar soluções inovadoras. Claro que, ao longo da sua jornada, essas bases podem ser revistas pelo seu grupo. Contudo, tente buscar o máximo de pensamento crítico na pesquisa para ganhar tempo lá na frente. E não se esqueça de considerar os conceitos iniciais de Governança de Dados e de viés, já abordados nos capítulos iniciais do primeiro ano.


> **Atenção:** buscar datasets públicos na internet é uma das tarefas mais desafiadoras para qualquer profissional de IA, especialmente quando o tema envolve áreas sensíveis como saúde, finanças, educação e dados pessoais. Muitos desses dados são protegidos por questões éticas, legais e de privacidade, tornando sua disponibilização pública extremamente restrita.

Mesmo quando os dados existem, é normal que estejam espalhados em repositórios pouco conhecidos, formatos desorganizados ou exigem processos de autorização para acesso.

É importante que vocês, alunos, compreendam que essa dificuldade faz parte natural do trabalho em IA: encontrar, limpar e preparar dados é uma das etapas mais demoradas e valiosas do projeto, e desistir logo nas primeiras buscas seria como abandonar um experimento antes mesmo de montar o laboratório. Persistência, criatividade e capacidade de buscar alternativas (como gerar dados simulados ou combinar fontes diferentes) são habilidades essenciais que vocês estão começando a desenvolver aqui — e isso vale tanto quanto o código em si.
 
**Atividade detalhada:**

**Parte 1 – Dados Numéricos (IoT):**

Busque e organize um pequeno dataset (mínimo 100 linhas) contendo variáveis como idade, sexo, pressão arterial, colesterol, histórico de doenças cardíacas, sintomas, frequência cardíaca etc.

> **Atenção:** o formato deverá ser .csv ou .xlsx

Organize seu dataset em um repositório no GitHub e, no arquivo README.md, inclua o link para os dados hospedados no seu OneDrive, Google Drive ou outro serviço de armazenamento público de sua escolha. No mesmo README.md, explique de forma clara a origem dos dados (se são reais ou simulados) e destaque quais variáveis você considera mais relevantes do ponto de vista clínico, justificando por que elas são importantes para um projeto de Inteligência Artificial voltado à saúde.
 
**Parte 2 – Dados Textuais (NLP):**

Faça o download de no mínimo dois textos (.txt) relacionados às doenças cardíacas, à saúde pública, aos sintomas ou aos tratamentos, usando fontes como SciELO, BVS, artigos do SUS ou mesmo literatura clássica (Projeto Gutenberg).

No mesmo repositório, adicione esses arquivos em uma subpasta “assets” ou “docs”, e, no mesmo README.md principal, explique de forma clara como esses textos podem ser explorados por algoritmos de NLP (por exemplo: análise de sentimentos, extração de sintomas, classificação de tópicos) e justifique por que essas análises são relevantes para um projeto de Inteligência Artificial aplicado à área da saúde.
 
**Parte 3 – Dados Visuais (VC):**

Reúna no mínimo 100 imagens de sua escolha (.jpg ou .png) de um tipo de exame cardiológico, como ECGs, angiogramas ou raio-X torácico.

No mesmo repositório do seu GitHub e, no mesmo arquivo README.md, inclua o link para as imagens hospedadas no seu OneDrive, Google Drive ou outro serviço de armazenamento público de sua escolha. Adicione uma justificativa que explique de forma clara como essas imagens poderão ser analisadas por algoritmos de Visão Computacional (por exemplo: detecção de padrões, identificação de bordas, reconhecimento de anomalias) e destaque a importância dessas análises para projetos de IA aplicados à área da saúde.
 
**Entregáveis:**

É necessário que o repositório do GitHub contenha:

- **Um arquivo README.md detalhado que explique o projeto, descreva cada uma das três partes, e indique os objetivos e as fontes dos dados;**
- **Subpasta docs ou assets e conteúdos;**

Links públicos (do Google Drive ou OneDrive ou semelhantes) apontando para o conjunto completo de dados preparados (numéricos, textuais e visuais). Garanta que o link esteja acessível para qualquer pessoa, para que o time da FIAP possa acessá-lo para a correção.

> **Dica:** caso queira, já organize pastas no repositório para armazenar os notebooks futuros que vão consumir esses dados no Colab ou Jupyter.

**Critérios de Avaliação (10 pontos totais):**

| **Critério** | **Pontos** |
| --- | --- |
| Parte 1 - Dataset numérico entregue corretamente, organizado e explicado. | 3 |
| Parte 2 - Textos selecionados e contextualizados corretamente | 2 |
| Parte 3 - Imagens entregues e bem justificadas em seu potencial para análise por IA. | 2 |
| Documento resumo com explicações claras, objetivas e bem estruturadas. | 2 |
| Cumprimento das orientações gerais e prazo de entrega. | 1 |

**Mensagem final:**

Lembre-se: nesta fase, não estamos apenas coletando dados, estamos construindo as bases para uma simulação de ecossistema de cardiologia inteligente. Tenha sempre atenção à relevância clínica das informações e pense sempre no impacto positivo que essas soluções podem trazer para a vida real.