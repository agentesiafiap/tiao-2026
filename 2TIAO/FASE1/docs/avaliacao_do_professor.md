NOTA: 17.5 de 18

FEEDBACK DO PROFESSOR
A entrega apresenta um trabalho excelente e bastante acima do mínimo solicitado para a Fase 1 do CardioIA. Foram encontrados 1.025 registros numéricos, uma base temporal adicional com 125 mil eventos, 13 documentos textuais e 230 imagens médicas efetivamente presentes no projeto, além de um acervo visual muito maior documentado no Google Drive. O grupo também demonstra preocupação com fontes, governança, desbalanceamento e aplicações futuras de cada modalidade. Os pequenos descontos estão relacionados principalmente à profundidade da análise de viés e à rastreabilidade/reprodutibilidade de algumas etapas de preparação.

Pontos positivos:
A base numérica principal possui 1.025 registros e 15 colunas, superando amplamente o mínimo de 100 registros.
O CSV está efetivamente presente na entrega e a quantidade informada no README corresponde ao arquivo analisado.
As variáveis são adequadas ao domínio cardiovascular, incluindo idade, sexo, tipo de dor torácica, pressão arterial, colesterol, glicemia, ECG, frequência cardíaca máxima, angina, segmento ST, vasos, talassemia e diagnóstico.
O grupo apresenta uma análise exploratória inicial, discutindo balanceamento do diagnóstico, correlações e valores extremos.
O diagnóstico está aproximadamente equilibrado, com 51,3% positivos e 48,7% negativos.
A fonte numérica é identificada como Heart Disease Dataset, UCI/Kaggle.
Além do requisito obrigatório, o grupo adicionou uma base de séries temporais com 125.000 registros, simulando monitoramento de sinais vitais.
Essa base possui identificador, timestamp, frequência cardíaca, pressão sistólica, pressão diastólica e evento, apresentando boa relação com o componente de IoT do CardioIA.
A documentação diferencia corretamente os dados clínicos estruturados dos dados temporais sintéticos.
Na parte de NLP, foram encontrados 13 arquivos .txt, muito acima dos dois exigidos.
O corpus combina diretrizes científicas, materiais para pacientes, FAQs, guia clínico e cartilhas.
Foram utilizadas referências da Sociedade Brasileira de Cardiologia, AHA/ACC e Ministério da Saúde.
A documentação é transparente ao informar quais textos foram elaborados pelo próprio grupo para fins acadêmicos.
Há boa diversidade de registro linguístico, combinando conteúdo técnico e material em linguagem mais acessível.
As aplicações propostas para NLP são coerentes, incluindo NER, classificação temática, FAQ, chatbot e exploração de informações clínicas.
Na parte visual, foram encontradas 230 imagens PNG efetivamente dentro do ZIP.
Dessas, 170 são imagens de ECG, distribuídas entre seis categorias.
Também foram entregues 60 radiografias torácicas, divididas entre presença e ausência de cardiomegalia.
Portanto, mesmo desconsiderando o armazenamento externo, o requisito mínimo de 100 imagens de um mesmo tipo de exame já é atendido pelo conjunto de ECG.
A escolha das imagens possui forte relação com cardiologia, tanto para análise de traçados eletrocardiográficos quanto para avaliação de cardiomegalia em radiografias.
O ECG contempla classes como batimento normal, ectópico supraventricular, ectópico ventricular, fusão, não classificável e infarto do miocárdio.
O README reconhece corretamente o forte desbalanceamento do conjunto completo de ECG e explica o risco de modelos favorecerem a classe normal.
O grupo relaciona esse problema a métricas importantes, como baixo recall em classes minoritárias.
O conjunto externo documentado é muito expressivo, com aproximadamente 124 mil imagens de ECG e 5,5 mil radiografias.
O README fornece link público do Google Drive para acesso aos conjuntos completos.
O documento docs/fontes.md centraliza adequadamente a procedência das diferentes modalidades.
A estrutura de diretórios é muito bem organizada entre dados numéricos, temporais, textos, ECG, radiografias e documentação.
A entrega demonstra planejamento para utilização dos dados em etapas futuras de Machine Learning, IoT, NLP e Visão Computacional.
A documentação aborda privacidade e informa que as bases utilizadas são desidentificadas.
Há preocupação explícita com vieses relacionados à sub-representação de determinados perfis clínicos.

Pontos a melhorar:
A discussão de governança e viés poderia ser mais quantitativa na base numérica, apresentando distribuição por sexo, idade, diagnóstico e outros grupos relevantes.
O fato de o diagnóstico estar aproximadamente 50/50 não significa que a base seja representativa da prevalência clínica real. Essa distinção deveria aparecer explicitamente.
A afirmação de que a diversidade do corpus e o grande número de imagens ajudam a reduzir viés precisa ser tratada com cuidado. Volume de dados não elimina viés de origem ou representatividade.
A base temporal sintética é interessante, mas deveria possuir documentação mais detalhada sobre as regras clínicas utilizadas para gerar eventos, crises hipertensivas e alterações de frequência cardíaca.
Seria importante manter no projeto o script responsável pela geração dos 125 mil registros temporais, permitindo reproduzir integralmente o conjunto.
A documentação poderia aprofundar as limitações demográficas e geográficas das bases UCI, MIT-BIH, PTB e dos conjuntos provenientes do Kaggle.
Para o conjunto visual, seria recomendável disponibilizar um manifesto com nome do arquivo, classe, origem e identificador do paciente ou exame, quando disponível.
Nas futuras divisões de treino, validação e teste, exames ou batimentos relacionados ao mesmo paciente ou registro original devem permanecer no mesmo conjunto, evitando vazamento de informação.
O README utiliza referências internas no formato [cite: 2] e [cite: 3], mas elas não estão apresentadas de maneira convencional ao leitor. Uma seção bibliográfica explícita deixaria a documentação mais profissional.
Embora o trabalho apresente dois tipos de exame visual, para esta fase bastava um. Nas próximas etapas será importante evitar dispersão e definir claramente qual modalidade será efetivamente utilizada para cada experimento.

Considerações finais:
Excelente entrega. O grupo não apenas atende aos requisitos da Fase 1, mas constrói um acervo multimodal bastante amplo, com dados estruturados, séries temporais, corpus textual diversificado e dois conjuntos de imagens cardiovasculares. Destacam-se especialmente os 1.025 registros numéricos, os 125 mil eventos temporais, os 13 textos, as 170 imagens de ECG presentes no próprio projeto e a identificação explícita do desbalanceamento das classes visuais. Para atingir um nível ainda mais rigoroso, o próximo avanço deve concentrar-se na rastreabilidade dos processos de geração e seleção dos dados e em uma análise quantitativa mais aprofundada dos vieses e da representatividade das diferentes fontes