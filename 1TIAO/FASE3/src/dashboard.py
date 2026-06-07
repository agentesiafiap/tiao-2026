"""
Dashboard de Monitoramento do Sistema de Irrigação Inteligente
Sistema desenvolvido para a Fase 3 do curso FIAP - Tecnologia em IA

Funcionalidades:
- Visualização dos níveis de umidade, P, K e pH
- Status da irrigação (relay_status)
- Sugestões de irrigação baseadas em dados climáticos
- Gráficos interativos e análises em tempo real
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import cx_Oracle
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy import create_engine
import urllib.parse

# Configuração da página
st.set_page_config(
    page_title="Sistema de Irrigação Inteligente - FIAP",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e7d4a 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f4e79;
    }
    .status-ok {
        color: #28a745;
        font-weight: bold;
    }
    .status-alert {
        color: #dc3545;
        font-weight: bold;
    }
    .irrigation-active {
        background-color: #d4edda;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    .irrigation-inactive {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Função para conectar ao Oracle (cx_Oracle tradicional)
@st.cache_resource
def init_connection():
    try:
        # Configurações de conexão Oracle
        username = "RM567686"
        password = "291278"
        host = "oracle.fiap.com.br"
        port = "1521"
        service_name = "ORCL"
        
        dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
        connection = cx_Oracle.connect(username, password, dsn)
        return connection
    except Exception as e:
        st.error(f"Erro ao conectar com o banco de dados: {e}")
        return None

# Função para executar consultas
@st.cache_data(ttl=300)  # Cache por 5 minutos
def run_query(query):
    try:
        conn = init_connection()
        if conn:
            # Suprimir warning do pandas temporariamente
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
                df = pd.read_sql(query, conn)
            conn.close()
            
            # Corrigir valores de umidade (dividir por 100 se necessário)
            if 'UMIDADE_DHT' in df.columns:
                df['UMIDADE_DHT'] = df['UMIDADE_DHT'] / 100
                
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao executar consulta: {e}")
        return pd.DataFrame()

# Função para converter timestamp Unix para datetime
def convert_timestamp(df):
    if not df.empty and 'TIMESTAMP' in df.columns:
        try:
            df['DATETIME'] = pd.to_datetime(df['TIMESTAMP'], unit='s')
            df['DATA'] = df['DATETIME'].dt.date
            df['HORA'] = df['DATETIME'].dt.time
        except Exception as e:
            st.error(f"Erro ao converter timestamp: {e}")
    return df

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🌱 Sistema de Irrigação Inteligente</h1>
    <p>Monitoramento em Tempo Real | FIAP - Tecnologia em IA | Grupo 16</p>
</div>
""", unsafe_allow_html=True)

# Sidebar com controles
st.sidebar.title("⚙️ Controles do Dashboard")
st.sidebar.markdown("---")

# Seletor de período de análise (relativo aos dados)
periodo_opcoes = {
    "Últimos 100 registros": 100,
    "Últimos 500 registros": 500,
    "Últimos 1000 registros": 1000,
    "Últimos 24 horas (dos dados)": "24h",
    "Últimos 3 dias (dos dados)": "3d", 
    "Última semana (dos dados)": "7d",
    "Todos os dados": 0
}
periodo_selecionado = st.sidebar.selectbox(
    "📅 Período de Análise:",
    list(periodo_opcoes.keys()),
    index=1
)

# Atualização automática
auto_refresh = st.sidebar.checkbox("🔄 Atualização Automática (30s)", value=False)
if auto_refresh:
    st.rerun()

# Botão de atualização manual
if st.sidebar.button("🔄 Atualizar Dados", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Informações do Sistema")
st.sidebar.info("**Banco:** Oracle FIAP\n**Tabela:** historico2024\n**Período:** Janeiro-Dezembro 2024\n**Status:** 🟢 Conectado")

# Informação sobre filtros
st.sidebar.markdown("### ℹ️ Sobre os Filtros")
st.sidebar.markdown("""
**Filtros por Registros:**
- Mostra os N registros mais recentes

**Filtros Temporais:**
- Relativos à data mais recente dos dados
- Dados de 2024 (não tempo atual)
""")

# Consulta principal dos dados (relativa aos dados existentes)
filtro_selecionado = periodo_opcoes[periodo_selecionado]

if filtro_selecionado == 0:
    # Todos os dados
    query = "SELECT * FROM historico2024 ORDER BY timestamp DESC"
elif isinstance(filtro_selecionado, int):
    # Filtro por número de registros
    query = f"""
    SELECT * FROM (
        SELECT * FROM historico2024 
        ORDER BY timestamp DESC
    ) WHERE ROWNUM <= {filtro_selecionado}
    ORDER BY timestamp DESC
    """
else:
    # Filtro temporal relativo aos dados (24h, 3d, 7d)
    if filtro_selecionado == "24h":
        query = """
        SELECT * FROM historico2024 
        WHERE timestamp >= (
            SELECT MAX(timestamp) - 86400 FROM historico2024
        )
        ORDER BY timestamp DESC
        """
    elif filtro_selecionado == "3d":
        query = """
        SELECT * FROM historico2024 
        WHERE timestamp >= (
            SELECT MAX(timestamp) - (3 * 86400) FROM historico2024
        )
        ORDER BY timestamp DESC
        """
    elif filtro_selecionado == "7d":
        query = """
        SELECT * FROM historico2024 
        WHERE timestamp >= (
            SELECT MAX(timestamp) - (7 * 86400) FROM historico2024
        )
        ORDER BY timestamp DESC
        """

# Carregamento dos dados
with st.spinner("Carregando dados do sistema de irrigação..."):
    df = run_query(query)

if df.empty:
    st.error("❌ Nenhum dado encontrado. Verifique a conexão com o banco de dados.")
    st.stop()

# Informação sobre dados carregados
st.sidebar.success(f"✅ {len(df):,} registros carregados")

# Processamento dos dados
df = convert_timestamp(df)
df_recente = df.head(1).iloc[0] if not df.empty else None

# Informações sobre o período dos dados carregados
if not df.empty and 'DATETIME' in df.columns:
    data_mais_antiga = df['DATETIME'].min()
    data_mais_recente = df['DATETIME'].max()
    total_registros = len(df)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 Período dos Dados Carregados")
    st.sidebar.markdown(f"""
    **📊 Total:** {total_registros:,} registros
    **📅 De:** {data_mais_antiga.strftime('%d/%m/%Y %H:%M')}
    **📅 Até:** {data_mais_recente.strftime('%d/%m/%Y %H:%M')}
    **⏱️ Intervalo:** {(data_mais_recente - data_mais_antiga).days} dias
    """)

# Métricas principais em tempo real
st.markdown("## 📊 Status Atual do Sistema")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if df_recente is not None:
        umidade_atual = df_recente['UMIDADE_DHT']
        delta_umidade = umidade_atual - df['UMIDADE_DHT'].mean()
        st.metric(
            label="💧 Umidade Atual",
            value=f"{umidade_atual:.1f}%",
            delta=f"{delta_umidade:.1f}%"
        )

with col2:
    if df_recente is not None:
        status_irrigacao = "🟢 ATIVO" if df_recente['RELAY_STATUS'] == 1 else "🔴 INATIVO"
        st.metric(
            label="🚿 Sistema de Irrigação",
            value=status_irrigacao
        )

with col3:
    if df_recente is not None:
        npk_status = "✅ OK" if df_recente['NPK_OK'] == 1 else "⚠️ ALERTA"
        st.metric(
            label="🧪 Nutrientes NPK",
            value=npk_status
        )

with col4:
    if df_recente is not None:
        ph_status = "✅ OK" if df_recente['PH_OK'] == 1 else "⚠️ ALERTA"
        st.metric(
            label="⚖️ Nível de pH",
            value=ph_status
        )

# Sistema de alertas
st.markdown("## 🚨 Central de Alertas")

col_alert1, col_alert2 = st.columns(2)

with col_alert1:
    if df_recente is not None:
        if df_recente['UMIDADE_BAIXA'] == 1:
            st.markdown("""
            <div class="irrigation-inactive">
                <h4>⚠️ ALERTA: Umidade Baixa Detectada</h4>
                <p>O solo está com baixa umidade. O sistema de irrigação deve ser ativado.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="irrigation-active">
                <h4>✅ Umidade do Solo Adequada</h4>
                <p>Os níveis de umidade estão dentro do esperado.</p>
            </div>
            """, unsafe_allow_html=True)

with col_alert2:
    if df_recente is not None:
        if df_recente['RELAY_STATUS'] == 1:
            st.markdown("""
            <div class="irrigation-active">
                <h4>🚿 Sistema de Irrigação ATIVO</h4>
                <p>O sistema está irrigando o solo no momento.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="irrigation-inactive">
                <h4>⏸️ Sistema de Irrigação INATIVO</h4>
                <p>O sistema não está irrigando no momento.</p>
            </div>
            """, unsafe_allow_html=True)

# Gráficos principais
st.markdown("## 📈 Análise Temporal dos Dados")

# Gráfico de umidade ao longo do tempo
fig_umidade = px.line(
    df.head(100), 
    x='DATETIME', 
    y='UMIDADE_DHT',
    title="💧 Evolução da Umidade do Solo",
    labels={'UMIDADE_DHT': 'Umidade (%)', 'DATETIME': 'Data e Hora'},
    color_discrete_sequence=['#1f77b4']
)
fig_umidade.add_hline(
    y=60, 
    line_dash="dash", 
    line_color="green",
    annotation_text="Nível Ideal (60%)"
)
fig_umidade.add_hline(
    y=40, 
    line_dash="dash", 
    line_color="red",
    annotation_text="Nível Crítico (40%)"
)
fig_umidade.update_layout(height=400)
st.plotly_chart(fig_umidade, width='stretch')

# Gráficos combinados
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    # Gráfico do status da irrigação
    irrigacao_dados = df['RELAY_STATUS'].value_counts()
    fig_irrigacao = px.pie(
        values=irrigacao_dados.values,
        names=['Inativo', 'Ativo'],
        title="🚿 Distribuição do Status de Irrigação",
        color_discrete_sequence=['#ff7f7f', '#90ee90']
    )
    st.plotly_chart(fig_irrigacao, width='stretch')

with col_graf2:
    # Gráfico dos nutrientes NPK
    npk_data = {
        'Nutriente': ['Nitrogênio (N)', 'Fósforo (P)', 'Potássio (K)'],
        'Presença (%)': [
            (df['N_PRESENTE'].sum() / len(df)) * 100,
            (df['P_PRESENTE'].sum() / len(df)) * 100,
            (df['K_PRESENTE'].sum() / len(df)) * 100
        ]
    }
    fig_npk = px.bar(
        npk_data,
        x='Nutriente',
        y='Presença (%)',
        title="🧪 Presença de Nutrientes NPK",
        color='Presença (%)',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_npk, width='stretch')

# Análise de correlação
st.markdown("## 🔍 Análise Avançada")

col_analise1, col_analise2 = st.columns(2)

with col_analise1:
    # Gráfico de dispersão: Umidade vs LDR
    fig_scatter = px.scatter(
        df.head(200),
        x='UMIDADE_DHT',
        y='LDR_VALOR',
        color='RELAY_STATUS',
        title="💡 Relação: Umidade vs Luminosidade",
        labels={
            'UMIDADE_DHT': 'Umidade (%)',
            'LDR_VALOR': 'Luminosidade',
            'RELAY_STATUS': 'Irrigação'
        },
        color_discrete_map={0: 'red', 1: 'green'}
    )
    st.plotly_chart(fig_scatter, width='stretch')

with col_analise2:
    # Heatmap de correlação
    correlacao_cols = ['UMIDADE_DHT', 'LDR_VALOR', 'RELAY_STATUS', 'UMIDADE_BAIXA']
    corr_matrix = df[correlacao_cols].corr()
    
    fig_heatmap = px.imshow(
        corr_matrix,
        title="🔥 Mapa de Correlação entre Variáveis",
        color_continuous_scale='RdYlBu',
        aspect='auto'
    )
    fig_heatmap.update_layout(height=400)
    st.plotly_chart(fig_heatmap, width='stretch')

# Sugestões inteligentes
st.markdown("## 🤖 Sugestões Inteligentes de Irrigação")

# Calcular métricas para sugestões
umidade_media = df['UMIDADE_DHT'].mean()
taxa_irrigacao = (df['RELAY_STATUS'].sum() / len(df)) * 100
luz_media = df['LDR_VALOR'].mean()

col_sug1, col_sug2, col_sug3 = st.columns(3)

with col_sug1:
    st.markdown("""
    ### 💧 Análise de Umidade
    """)
    if umidade_media < 45:
        st.warning(f"**Atenção:** Umidade média baixa ({umidade_media:.1f}%). Considere aumentar a frequência de irrigação.")
    elif umidade_media > 75:
        st.info(f"**OK:** Umidade média adequada ({umidade_media:.1f}%). Sistema funcionando bem.")
    else:
        st.success(f"**Excelente:** Umidade média ideal ({umidade_media:.1f}%). Continue monitorando.")

with col_sug2:
    st.markdown("""
    ### 🚿 Eficiência da Irrigação
    """)
    if taxa_irrigacao < 10:
        st.success(f"**Ótimo:** Sistema eficiente ({taxa_irrigacao:.1f}% de ativação). Solo bem gerenciado.")
    elif taxa_irrigacao > 30:
        st.warning(f"**Atenção:** Alta ativação ({taxa_irrigacao:.1f}%). Verifique vazamentos ou ajuste sensores.")
    else:
        st.info(f"**Normal:** Ativação moderada ({taxa_irrigacao:.1f}%). Sistema equilibrado.")

with col_sug3:
    st.markdown("""
    ### ☀️ Condições Ambientais
    """)
    if luz_media > 2000:
        st.info(f"**Dia ensolarado:** Alta luminosidade ({luz_media:.0f}). Monitore evaporação.")
    elif luz_media < 1500:
        st.info(f"**Condições nubladas:** Baixa luminosidade ({luz_media:.0f}). Menos evaporação esperada.")
    else:
        st.success(f"**Condições ideais:** Luminosidade equilibrada ({luz_media:.0f}).")

# Tabela de dados recentes
st.markdown("## 📋 Registros Mais Recentes")

# Preparar dados para exibição
df_display = df.head(10).copy()
df_display = df_display[['DATETIME', 'UMIDADE_DHT', 'LDR_VALOR', 'N_PRESENTE', 
                        'P_PRESENTE', 'K_PRESENTE', 'RELAY_STATUS', 'UMIDADE_BAIXA', 
                        'NPK_OK', 'PH_OK']]

# Renomear colunas para melhor visualização
df_display.columns = ['Data/Hora', 'Umidade (%)', 'Luminosidade', 'N', 'P', 'K', 
                     'Irrigação', 'Umidade Baixa', 'NPK OK', 'pH OK']

st.dataframe(df_display, width='stretch')

# Estatísticas resumidas
st.markdown("## 📊 Estatísticas do Sistema")

col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)

with col_stats1:
    st.metric("📈 Total de Registros", len(df))

with col_stats2:
    st.metric("💧 Umidade Média", f"{df['UMIDADE_DHT'].mean():.1f}%")

with col_stats3:
    st.metric("🚿 Ativações Totais", df['RELAY_STATUS'].sum())

with col_stats4:
    st.metric("⚠️ Alertas de Umidade", df['UMIDADE_BAIXA'].sum())

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
    <p>🌱 Sistema de Irrigação Inteligente | FIAP - Tecnologia em IA | Grupo 16 - Oracle</p>
    <p>Dashboard desenvolvido com Streamlit | Dados atualizados em tempo real</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()