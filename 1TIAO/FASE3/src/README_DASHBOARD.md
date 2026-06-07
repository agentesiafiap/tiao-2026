# SRC - Sistema de Irrigação Inteligente

## Sobre o Dashboard

O Dashboard de Irrigação Inteligente foi desenvolvido para visualizar em tempo real os dados coletados pelos sensores do sistema de irrigação. Oferece duas opções de interface:

1. **Streamlit** (Recomendado): Interface moderna e interativa
2. **Dash/Plotly**: Alternativa com mais controle sobre layout

## 📋 Pré-requisitos

### 1. Python
- Python 3.8 ou superior instalado
- pip (gerenciador de pacotes) atualizado

### 2. Oracle Instant Client (Para conexão com banco)
- Faça download do Oracle Instant Client em: https://www.oracle.com/database/technologies/instant-client.html
- Extraia e configure as variáveis de ambiente conforme sua plataforma

### 3. Credenciais do Banco
- **Host**: oracle.fiap.com.br
- **Usuário**: RM567686  
- **Senha**: 291278
- **Tabela**: historico2024

## 🔧 Instalação

### Passo 1: Clone/Baixe o Projeto
```bash
# Se usando git
git clone [URL_DO_REPOSITORIO]
cd cursotiaos-fase3-grupo16-oracle-temp

# Ou extraia o arquivo ZIP baixado
```

### Passo 2: Instale as Dependências
```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Ou instalar individualmente:
pip install streamlit pandas plotly cx_Oracle dash numpy python-dateutil requests
```

### Passo 3: Verificar Conexão Oracle
```bash
# Teste a conexão (opcional)
python -c "import cx_Oracle; print('Oracle Client instalado com sucesso!')"
```

## ▶️ Executando o Dashboard

### Opção 1: Dashboard Streamlit (Recomendado)
```bash
# Navegar até a pasta do projeto
cd /caminho/para/cursotiaos-fase3-grupo16-oracle-temp

# Executar o dashboard principal
streamlit run src/dashboard.py
```

**Resultado**: O dashboard abrirá automaticamente no navegador em `http://localhost:8501`

### Opção 2: Dashboard Dash (Alternativo)
```bash
# Executar dashboard alternativo
python src/dashboard_dash.py
```

**Resultado**: Acesse manualmente `http://localhost:8050` no navegador

## 🎯 Funcionalidades Detalhadas do Dashboard

### 📊 Métricas em Tempo Real
- **Umidade Atual**: Valor instantâneo da umidade do solo
- **Status da Irrigação**: Se o sistema está ativo ou inativo
- **Nutrientes NPK**: Status dos nutrientes no solo
- **Nível de pH**: Condição do pH do solo

### 📈 Gráficos Interativos
1. **Evolução da Umidade**: Linha temporal mostrando variação da umidade
2. **Status da Irrigação**: Pizza mostrando distribuição ativo/inativo
3. **Presença de Nutrientes**: Barras com percentual de NPK
4. **Correlação Umidade vs Luminosidade**: Dispersão para análise de padrões

### 🤖 Sugestões Inteligentes
- Análise automática das condições
- Recomendações baseadas nos dados
- Alertas de umidade baixa
- Sugestões de eficiência do sistema

### ⚙️ Controles Disponíveis
- **Seletor de Período**: 
  - Por registros: 100, 500, 1000 mais recentes
  - Por tempo: Últimas 24h, 3 dias, 7 dias dos dados (relativos ao dataset de 2024)
- **Atualização Automática**: Refresh a cada 30 segundos
- **Botão Manual**: Atualização sob demanda
- **Tabela de Dados**: Registros mais recentes
- **Informações do Período**: Mostra intervalo de datas carregadas

## 📱 Usando o Dashboard

### Interface Streamlit
1. **Sidebar**: Controles de período e atualização
2. **Header**: Status atual do sistema
3. **Alertas**: Notificações importantes
4. **Gráficos**: Análises visuais dos dados
5. **Tabela**: Dados recentes em formato tabular
6. **Sugestões**: Recomendações inteligentes

### Navegação
- Use os controles da sidebar para filtrar dados
- Clique nos gráficos para interações (zoom, hover, etc.)
- Ative atualização automática para monitoramento contínuo
- Use o botão de atualização manual quando necessário

## � Configurações Técnicas

### Conexão Oracle
```python
# Configurações no código
username = "RM567686"
password = "291278"
host = "oracle.fiap.com.br"
port = "1521"
service_name = "ORCL"
tabela = "historico2024"
```

### Dependências Principais
- **Streamlit**: Framework do dashboard principal
- **Dash**: Framework alternativo
- **Plotly**: Gráficos interativos
- **Pandas**: Manipulação de dados
- **cx_Oracle**: Conexão com Oracle Database

## 🎥 Demonstração

Recursos ideais para mostrar no vídeo:
1. **Inicialização** do dashboard
2. **Métricas em tempo real** atualizando
3. **Gráficos interativos** (zoom, hover)
4. **Sistema de alertas** funcionando
5. **Sugestões inteligentes** sendo geradas
6. **Filtros temporais** alterando visualizações

## 🔗 Arquivos Relacionados
- Dados de entrada: `../assets/dados_historicos_2024.csv`
- Configuração Oracle: `../scripts/oracle_import.md`
- Consultas SQL: `../scripts/consultas_analise.sql`
- Dependências: `../requirements.txt`
- Documentação: `../README.md`

---
**🌱 Sistema desenvolvido para FIAP - Tecnologia em IA | Grupo 16**