<img src="../assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=30% height=30%>

# AI Project Document - Módulo 1 - FIAP

## Agentes IA Fiap

#### Nomes dos integrantes do grupo

Daniel Emilio Baião, Eric Criscuolo, Marcus Vinícius Loureiro Garcia, Sidney William de Paula Dias, Hugo Rodrigues Carvalho Silva.

## Sumário

[1. Introdução](#c1)
  - [1.1. Escopo do Projeto](#c1)
  - [1.2. Fundamentos Técnicos](#c1)

[2. Visão Geral do Projeto](#c2)
  - [2.1. Objetivos do Projeto](#c2)
  - [2.2. Público-Alvo](#c2)
  - [2.3. Metodologia](#c2)

[3. Desenvolvimento do Projeto](#c3)
  - [3.1. Tecnologias Utilizadas](#c3)
  - [3.2. Manipulação de Arquivos](#c3)
  - [3.3. Estruturas de Dados Utilizadas](#c3)
  - [3.4. Modelagem e Algoritmos](#c3)

[4. Resultados e Avaliações](#c4)

[5. Conclusões e Trabalhos Futuros](#c5)

[6. Referências](#c6)

[Anexos](#c7)

<br>

# <a name="c1"></a>1. Introdução

## 1.1. Escopo do Projeto

### 1.1.1. Contexto da Inteligência Artificial

A Inteligência Artificial (IA) tem desempenhado um papel crucial na modernização da agricultura, permitindo a análise de dados em tempo real, previsão de colheitas e otimização de recursos. Este projeto se insere no contexto da agricultura de precisão, utilizando IA para melhorar a eficiência e a produtividade agrícola.

### 1.1.2. Descrição da Solução Desenvolvida

A solução desenvolvida é um sistema integrado que permite o gerenciamento de dados agrícolas para cana-de-açúcar, focando especificamente no cálculo do BRIX e índice de maturação para determinar o momento ideal de colheita. O sistema integra coleta de dados, análise preditiva através de regressão linear e ferramentas de visualização para facilitar a tomada de decisão agrícola.

## 1.2. Fundamentos Técnicos

### 1.2.1. O que é BRIX na Cana-de-Açúcar

O BRIX (°Bx) é uma unidade de medida que indica a concentração de sólidos solúveis totais em uma solução, expressa em porcentagem de sacarose. Na cana-de-açúcar, o BRIX representa principalmente o teor de açúcar presente no caldo, sendo um indicador fundamental da qualidade e maturidade da cana.

**Importância do BRIX:**
- Determina o rendimento industrial da cana-de-açúcar
- Indica o momento ideal para colheita (máxima concentração de açúcar)
- Influencia diretamente a rentabilidade da produção
- Valores ideais para colheita: BRIX ≥ 18°

### 1.2.2. Índice de Maturação (IM)

O Índice de Maturação é calculado pela razão entre o BRIX da ponta e o BRIX da base da cana:
```
IM = BRIX_ponta / BRIX_base
```

**Interpretação do IM:**
- **IM > 1,0**: Cana madura, com maior concentração de açúcar na ponta
- **IM = 1,0**: Cana uniformemente madura
- **IM < 1,0**: Cana imatura, base com mais açúcar que a ponta
- **Valor ideal para colheita**: IM entre 0,95 e 1,05

### 1.2.3. Metodologia de Medição

O sistema coleta dados de três pontos da cana:
- **Base**: Porção inferior do colmo
- **Meio**: Porção central do colmo  
- **Ponta**: Porção superior do colmo

O BRIX médio é calculado pela média aritmética dos três pontos, fornecendo uma visão geral da maturação da cana.

# <a name="c2"></a>2. Visão Geral do Projeto

## 2.1. Objetivos do Projeto

### 2.1.1. Objetivos Principais
- Automatizar o cálculo de BRIX médio e Índice de Maturação com base em dados coletados da cana-de-açúcar
- Prever o momento ideal para a colheita utilizando regressão linear aplicada a dados temporais
- Facilitar a visualização da evolução da maturação através de gráficos interativos
- Armazenar e gerenciar dados de forma eficiente em banco de dados Oracle

### 2.1.2. Critérios Agronômicos para Colheita Ideal

**Parâmetros de Maturação:**

1. **BRIX ≥ 18°**
   - **Justificativa**: Valor mínimo para viabilidade econômica da moagem
   - **Impacto**: Abaixo de 18° o rendimento industrial é baixo
   - **Contexto**: Padrão da indústria sucroalcooleira brasileira

2. **Índice de Maturação (IM) entre 0,95 e 1,05**
   - **IM > 1,05**: Cana com ponta muito madura, possível deterioração
   - **IM 0,95-1,05**: Cana uniformemente madura (ideal)
   - **IM < 0,95**: Cana imatura, base com mais açúcar que ponta

**Cronograma de Maturação:**
- **Fase Vegetativa**: BRIX < 12°, IM irregular
- **Início da Maturação**: BRIX 12-16°, IM aproximando-se de 1,0
- **Maturação Ideal**: BRIX ≥ 18°, IM 0,95-1,05
- **Sobrematuração**: BRIX > 22°, possível perda de qualidade

**Fatores que Influenciam a Maturação:**
- Variedade da cana-de-açúcar
- Condições climáticas (temperatura e umidade)
- Manejo agrícola (irrigação, adubação)
- Idade da cana (primeira ou segunda soca)

## 2.2. Público-Alvo

O público-alvo do projeto inclui agricultores, cooperativas agrícolas e empresas do setor agroindustrial que buscam otimizar suas operações e aumentar a produtividade.

## 2.3. Metodologia

A metodologia utilizada no desenvolvimento do projeto seguiu as seguintes etapas:
1. **Definição de Requisitos**: Identificação das necessidades do usuário.
2. **Desenvolvimento do Sistema**: Implementação do código Python com funcionalidades específicas.
3. **Treinamento e Teste**: Validação dos algoritmos de previsão.
4. **Integração**: Conexão com banco de dados Oracle e ferramentas de visualização.
5. **Avaliação**: Testes com usuários finais para validação da solução.

# <a name="c3"></a>3. Desenvolvimento do Projeto

## 3.1. Tecnologias Utilizadas

- **Linguagem de Programação**: Python 3.x
- **Bibliotecas Principais**: 
  - `matplotlib`: Visualização de dados e geração de gráficos
  - `numpy`: Cálculos matemáticos e regressão linear
  - `oracledb`: Conexão e manipulação do banco Oracle
  - `json`: Manipulação de arquivos JSON
- **Banco de Dados**: Oracle Database 
- **Ferramentas de Desenvolvimento**: Visual Studio Code

## 3.2. Manipulação de Arquivos

### 3.2.1. Arquivos JSON
- **Arquivo**: `resultados_colheita.json`
- **Estrutura**: Lista de dicionários com dados de BRIX e IM
- **Funcionalidades**: 
  - `salvar_json()`: Exportação dos dados da memória
  - `carregar_json()`: Importação de dados históricos
- **Formato**:
```json
[
    {
        "Brix Base": 16.5,
        "Brix Meio": 17.2,
        "Brix Ponta": 15.8,
        "Brix Médio": 16.5,
        "Índice de Maturação": 0.96
    }
]
```

### 3.2.2. Arquivos de Texto
- **Arquivo**: `resultados_colheita.txt`
- **Formato**: Texto estruturado para relatórios
- **Funcionalidade**: `salvar_txt()` para exportação legível
- **Uso**: Backup e relatórios para usuários finais

## 3.2. Estruturas de Dados Utilizadas

### 3.2.1. Lista (List)
- **`memoria = []`**: Tabela de memória principal que armazena todos os resultados durante a execução
- **`leituras`**: Lista contendo os valores de BRIX (base, meio, ponta) para cálculo da média
- **Uso**: Armazenamento dinâmico, operações de append, pop e iteração

### 3.2.2. Tupla (Tuple)  
- **`(brix_base, brix_meio, brix_ponta)`**: Estrutura imutável para agrupamento dos três valores de BRIX
- **Uso**: Passagem de parâmetros para função `calcular_brix_medio()`

### 3.2.3. Dicionário (Dictionary)
- **Estrutura principal dos resultados**:
```python
{
    "Brix Base": valor,
    "Brix Meio": valor, 
    "Brix Ponta": valor,
    "Brix Médio": valor,
    "Índice de Maturação": valor
}
```
- **Uso**: Estruturação de dados com chaves descritivas, fácil acesso aos valores

### 3.2.4. Tabela de Memória
- **`memoria`**: Lista funcionando como tabela em memória com operações CRUD
- **Funcionalidades**: Inserção, consulta, remoção e carregamento de dados
- **Integração**: Sincronização com JSON e banco Oracle

## 3.3. Modelagem e Algoritmos

### 3.3.1. Subalgoritmos com Passagem de Parâmetros

**Funções Implementadas:**
- `calcular_brix_medio(leituras)`: Recebe lista de valores e retorna média aritmética
- `calcular_indice_maturacao(brix_base, brix_ponta)`: Calcula IM com dois parâmetros
- `gerar_grafico(memoria)`: Procedimento que recebe lista para visualização
- `prever_momento_colheita(memoria)`: Função de previsão com parâmetro de entrada

**Procedimentos:**
- `procedimento_calculo()`: Coleta dados do usuário e processa cálculos
- `salvar_json(lista)`, `salvar_txt(lista)`: Persistência de dados

### 3.3.2. Algoritmos de Previsão

**Regressão Linear Aplicada ao Contexto Agrícola:**
- **Método**: Ajuste polinomial de grau 1 (linear) usando `numpy.polyfit()`
- **Variáveis preditoras**: Dias de amostragem (tempo)
- **Variáveis resposta**: BRIX médio e Índice de Maturação
- **Projeção**: Previsão para 365 dias futuros
- **Critério de decisão**: BRIX ≥ 18° e IM entre 0,95-1,05

**Justificativa da Escolha:**
- Simplicidade e estabilidade para dados agrícolas
- Tendência linear natural do amadurecimento da cana
- Interpretabilidade dos resultados para produtores

### 3.3.3. Processamento de Dados
- **Entrada**: Valores de BRIX coletados manualmente
- **Processamento**: Cálculo de médias e índices
- **Saída**: Recomendação de data ideal para colheita

## 3.3. Treinamento e Teste

- **Conjuntos de Dados**: Dados inseridos manualmente.
- **Métricas de Avaliação**: Precisão das previsões e feedback dos usuários.
- **Resultados**: O sistema apresentou alta precisão na previsão do momento ideal de colheita.

# <a name="c4"></a>4. Resultados e Avaliações

## 4.1. Análise dos Resultados

### 4.1.1. Conformidade com Requisitos Acadêmicos

1. **Subalgoritmos (Funções e Procedimentos)**:
   - ✅ 8 funções com passagem de parâmetros implementadas
   - ✅ Procedimentos para entrada de dados e processamento
   - ✅ Modularização adequada do código

2. **Estruturas de Dados**:
   - ✅ **Lista**: `memoria[]` como tabela de memória principal
   - ✅ **Tupla**: Agrupamento de valores BRIX para cálculos
   - ✅ **Dicionário**: Estrutura de dados principal dos resultados
   - ✅ **Tabela de Memória**: Lista com operações CRUD completas

3. **Manipulação de Arquivos**:
   - ✅ **JSON**: Serialização e deserialização de dados
   - ✅ **Texto**: Geração de relatórios em formato TXT
   - ✅ Tratamento de erros e encoding UTF-8

4. **Conexão com Banco Oracle**:
   - ✅ Conexão segura com credenciais
   - ✅ Criação automática de tabelas
   - ✅ Operações CRUD completas (Create, Read, Update, Delete)

### 4.1.2. Resultados Funcionais

O sistema demonstrou capacidade de:
- **Processamento de Dados**: Cálculo preciso de BRIX médio e IM
- **Previsão**: Identificação do momento ideal de colheita através de regressão linear
- **Visualização**: Gráficos com dados históricos e projeções futuras
- **Persistência**: Armazenamento em múltiplos formatos (memória, JSON, TXT, Oracle)

### 4.1.3. Validação Agronômica

- **Precisão dos Cálculos**: Fórmulas validadas conforme padrões da indústria
- **Critérios de Maturação**: Implementação dos valores de referência (BRIX ≥ 18°, IM 0,95-1,05)
- **Aplicabilidade**: Solução adequada para produtores de cana-de-açúcar

### 4.1.4. Visualização dos Resultados

O sistema gera gráficos interativos que permitem:
- Acompanhamento da evolução temporal do BRIX e Índice de Maturação
- Projeções futuras baseadas em regressão linear para até 365 dias
- Identificação visual do momento ideal de colheita
- Comparação com valores de referência da indústria

*Ver Figura 1 na seção de [Anexos](#c7) para exemplo de visualização gerada pelo sistema.*

# <a name="c5"></a>5. Conclusões e Trabalhos Futuros

## 5.1. Conclusões

**Conformidade Técnica:**
- Implementação completa de subalgoritmos com passagem de parâmetros
- Utilização adequada de todas as estruturas de dados requeridas
- Manipulação eficiente de arquivos JSON e texto
- Conexão robusta com banco de dados Oracle

**Aplicação Prática:**
- Sistema funcional para determinação do momento ideal de colheita da cana-de-açúcar
- Cálculos precisos de BRIX e Índice de Maturação
- Interface intuitiva para produtores rurais
- Visualização clara da evolução da maturação

**Inovação Tecnológica:**
- Aplicação de regressão linear para previsão agrícola
- Integração de múltiplas formas de persistência de dados
- Modularização adequada facilitando manutenção e expansão

# <a name="c6"></a>6. Referências

- Documentação oficial do Python: https://docs.python.org/
- Biblioteca Matplotlib: https://matplotlib.org/
- Documentação do cx_Oracle: https://cx-oracle.readthedocs.io/

# <a name="c7"></a>Anexos

## Visualizações do Sistema

### Gráfico de Evolução e Projeção do BRIX e Índice de Maturação

O sistema gera automaticamente gráficos que mostram a evolução histórica dos dados coletados e projeções futuras baseadas em regressão linear. O gráfico abaixo demonstra:

- **Linha Azul**: Evolução histórica do BRIX médio
- **Linha Laranja**: Evolução histórica do Índice de Maturação
- **Linhas Tracejadas**: Projeções futuras (365 dias)
- **Linhas Pontilhadas**: Valores ideais de referência (BRIX = 18°, IM = 1.0)

<div align="center">
  <img src="../assets/Figure_1.png" alt="Gráfico de Evolução e Projeção do Brix e Índice de Maturação da Cana" width="80%">
  <p><em>Figura 1: Análise temporal do BRIX e Índice de Maturação com projeções preditivas</em></p>
</div>

### Interpretação do Gráfico

- **Zona Verde**: Período ideal para colheita (BRIX ≥ 18° e IM próximo de 1.0)
- **Tendências**: As linhas tracejadas indicam quando a cana atingirá maturação ideal
- **Precisão**: A regressão linear permite planejamento antecipado da colheita

## Tabelas

- Exemplo de dados armazenados no banco de dados Oracle:
  | Data       | Resultado | Previsão de Colheita |
  |------------|-----------|----------------------|
  | 2025-10-14 | 85%       | 2025-11-01          |
