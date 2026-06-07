"""
Dashboard Alternativo usando Dash/Plotly
Sistema de Irrigação Inteligente - FIAP Fase 3

Este é um exemplo alternativo de dashboard usando Dash ao invés de Streamlit
Para usar este dashboard, execute: python src/dashboard_dash.py
"""

import dash
from dash import html, dcc, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import cx_Oracle
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import urllib.parse

# Configurações de conexão Oracle
DB_CONFIG = {
    'username': 'RM567686',
    'password': '291278',
    'host': 'oracle.fiap.com.br',
    'port': '1521',
    'service_name': 'ORCL'
}

# Função para conectar ao banco (cx_Oracle tradicional)
def get_oracle_connection():
    try:
        dsn = cx_Oracle.makedsn(
            DB_CONFIG['host'], 
            DB_CONFIG['port'], 
            service_name=DB_CONFIG['service_name']
        )
        connection = cx_Oracle.connect(
            DB_CONFIG['username'], 
            DB_CONFIG['password'], 
            dsn
        )
        return connection
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

# Função para buscar dados (relativa aos dados existentes)
def fetch_data(filtro_tipo="500_registros"):
    try:
        conn = get_oracle_connection()
        if not conn:
            return pd.DataFrame()
        
        # Definir query baseada no tipo de filtro
        if filtro_tipo == "100_registros":
            query = """
            SELECT * FROM (
                SELECT * FROM historico2024 ORDER BY timestamp DESC
            ) WHERE ROWNUM <= 100
            ORDER BY timestamp DESC
            """
        elif filtro_tipo == "500_registros":
            query = """
            SELECT * FROM (
                SELECT * FROM historico2024 ORDER BY timestamp DESC
            ) WHERE ROWNUM <= 500
            ORDER BY timestamp DESC
            """
        elif filtro_tipo == "24h_dados":
            query = """
            SELECT * FROM historico2024 
            WHERE timestamp >= (
                SELECT MAX(timestamp) - 86400 FROM historico2024
            )
            ORDER BY timestamp DESC
            """
        elif filtro_tipo == "3d_dados":
            query = """
            SELECT * FROM historico2024 
            WHERE timestamp >= (
                SELECT MAX(timestamp) - (3 * 86400) FROM historico2024
            )
            ORDER BY timestamp DESC
            """
        elif filtro_tipo == "7d_dados":
            query = """
            SELECT * FROM historico2024 
            WHERE timestamp >= (
                SELECT MAX(timestamp) - (7 * 86400) FROM historico2024
            )
            ORDER BY timestamp DESC
            """
        else:
            # Todos os dados (limitado a 1000 para performance)
            query = """
            SELECT * FROM (
                SELECT * FROM historico2024 ORDER BY timestamp DESC
            ) WHERE ROWNUM <= 1000
            ORDER BY timestamp DESC
            """
        
        # Suprimir warning do pandas
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
            df = pd.read_sql(query, conn)
        conn.close()
        
        # Corrigir valores de umidade e converter timestamp
        if not df.empty:
            if 'UMIDADE_DHT' in df.columns:
                df['UMIDADE_DHT'] = df['UMIDADE_DHT'] / 100
            if 'TIMESTAMP' in df.columns:
                df['DATETIME'] = pd.to_datetime(df['TIMESTAMP'], unit='s')
        
        return df
        
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()

# Inicializar app Dash
app = dash.Dash(__name__)
app.title = "Sistema de Irrigação Inteligente - FIAP"

# Layout do dashboard
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🌱 Sistema de Irrigação Inteligente", 
                className="header-title"),
        html.P("FIAP - Tecnologia em IA | Grupo 16 | Dashboard em Tempo Real",
               className="header-subtitle")
    ], className="header"),
    
    # Controles
    html.Div([
        html.Label("Período de Análise:"),
        dcc.Dropdown(
            id='periodo-dropdown',
            options=[
                {'label': 'Últimos 100 registros', 'value': '100_registros'},
                {'label': 'Últimos 500 registros', 'value': '500_registros'},
                {'label': 'Últimas 24h (dos dados)', 'value': '24h_dados'},
                {'label': 'Últimos 3 dias (dos dados)', 'value': '3d_dados'},
                {'label': 'Última semana (dos dados)', 'value': '7d_dados'},
                {'label': 'Todos os dados', 'value': 'todos'}
            ],
            value='500_registros',
            style={'width': '250px', 'display': 'inline-block'}
        ),
        html.Button('🔄 Atualizar', id='refresh-button', 
                   style={'margin-left': '20px'})
    ], className="controls"),
    
    # Métricas principais
    html.Div(id='metricas-principais', className="metrics-row"),
    
    # Gráficos
    html.Div([
        html.Div([
            dcc.Graph(id='grafico-umidade')
        ], className="chart-container"),
        
        html.Div([
            dcc.Graph(id='grafico-npk')
        ], className="chart-container")
    ], className="charts-row"),
    
    html.Div([
        html.Div([
            dcc.Graph(id='grafico-irrigacao')
        ], className="chart-container"),
        
        html.Div([
            dcc.Graph(id='grafico-correlacao')
        ], className="chart-container")
    ], className="charts-row"),
    
    # Tabela de dados
    html.Div([
        html.H3("📋 Dados Mais Recentes"),
        html.Div(id='tabela-dados')
    ], className="table-container"),
    
    # Sugestões
    html.Div(id='sugestoes', className="suggestions"),
    
    # Intervalo para atualização automática
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # 30 segundos
        n_intervals=0
    ),
    
    # Store para dados
    dcc.Store(id='data-store')
])

# Callback para atualizar dados
@app.callback(
    Output('data-store', 'data'),
    [Input('periodo-dropdown', 'value'),
     Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_data(filtro_periodo, n_clicks, n_intervals):
    df = fetch_data(filtro_periodo)
    return df.to_dict('records')

# Callback para métricas principais
@app.callback(
    Output('metricas-principais', 'children'),
    [Input('data-store', 'data')]
)
def update_metricas(data):
    if not data:
        return html.Div("Carregando dados...")
    
    df = pd.DataFrame(data)
    if df.empty:
        return html.Div("Nenhum dado disponível")
    
    # Dados mais recentes
    ultimo_registro = df.iloc[0]
    
    metricas = html.Div([
        html.Div([
            html.H4(f"{ultimo_registro['UMIDADE_DHT']:.1f}%"),
            html.P("💧 Umidade Atual")
        ], className="metric-card"),
        
        html.Div([
            html.H4("🟢 ATIVO" if ultimo_registro['RELAY_STATUS'] == 1 else "🔴 INATIVO"),
            html.P("🚿 Irrigação")
        ], className="metric-card"),
        
        html.Div([
            html.H4("✅ OK" if ultimo_registro['NPK_OK'] == 1 else "⚠️ ALERTA"),
            html.P("🧪 NPK Status")
        ], className="metric-card"),
        
        html.Div([
            html.H4("✅ OK" if ultimo_registro['PH_OK'] == 1 else "⚠️ ALERTA"),
            html.P("⚖️ pH Status")
        ], className="metric-card")
    ], className="metrics-container")
    
    return metricas

# Callback para gráfico de umidade
@app.callback(
    Output('grafico-umidade', 'figure'),
    [Input('data-store', 'data')]
)
def update_grafico_umidade(data):
    if not data:
        return {}
    
    df = pd.DataFrame(data)
    if df.empty:
        return {}
    
    df['DATETIME'] = pd.to_datetime(df['TIMESTAMP'], unit='s')
    
    fig = px.line(
        df, 
        x='DATETIME', 
        y='UMIDADE_DHT',
        title='💧 Evolução da Umidade do Solo',
        labels={'UMIDADE_DHT': 'Umidade (%)', 'DATETIME': 'Data/Hora'}
    )
    
    # Linhas de referência
    fig.add_hline(y=60, line_dash="dash", line_color="green", 
                  annotation_text="Ideal (60%)")
    fig.add_hline(y=40, line_dash="dash", line_color="red", 
                  annotation_text="Crítico (40%)")
    
    return fig

# Callback para gráfico NPK
@app.callback(
    Output('grafico-npk', 'figure'),
    [Input('data-store', 'data')]
)
def update_grafico_npk(data):
    if not data:
        return {}
    
    df = pd.DataFrame(data)
    if df.empty:
        return {}
    
    npk_data = {
        'Nutriente': ['Nitrogênio (N)', 'Fósforo (P)', 'Potássio (K)'],
        'Presença (%)': [
            (df['N_PRESENTE'].sum() / len(df)) * 100,
            (df['P_PRESENTE'].sum() / len(df)) * 100,
            (df['K_PRESENTE'].sum() / len(df)) * 100
        ]
    }
    
    fig = px.bar(
        npk_data,
        x='Nutriente',
        y='Presença (%)',
        title='🧪 Presença de Nutrientes NPK',
        color='Presença (%)',
        color_continuous_scale='Viridis'
    )
    
    return fig

# Callback para gráfico de irrigação
@app.callback(
    Output('grafico-irrigacao', 'figure'),
    [Input('data-store', 'data')]
)
def update_grafico_irrigacao(data):
    if not data:
        return {}
    
    df = pd.DataFrame(data)
    if df.empty:
        return {}
    
    irrigacao_counts = df['RELAY_STATUS'].value_counts()
    
    fig = px.pie(
        values=irrigacao_counts.values,
        names=['Inativo', 'Ativo'],
        title='🚿 Status da Irrigação',
        color_discrete_sequence=['#ff9999', '#66b3ff']
    )
    
    return fig

# Callback para gráfico de correlação
@app.callback(
    Output('grafico-correlacao', 'figure'),
    [Input('data-store', 'data')]
)
def update_grafico_correlacao(data):
    if not data:
        return {}
    
    df = pd.DataFrame(data)
    if df.empty:
        return {}
    
    fig = px.scatter(
        df,
        x='UMIDADE_DHT',
        y='LDR_VALOR',
        color='RELAY_STATUS',
        title='💡 Umidade vs Luminosidade',
        labels={'UMIDADE_DHT': 'Umidade (%)', 'LDR_VALOR': 'Luminosidade'},
        color_discrete_map={0: 'red', 1: 'green'}
    )
    
    return fig

# Callback para tabela
@app.callback(
    Output('tabela-dados', 'children'),
    [Input('data-store', 'data')]
)
def update_tabela(data):
    if not data:
        return html.Div("Carregando...")
    
    df = pd.DataFrame(data)
    if df.empty:
        return html.Div("Nenhum dado disponível")
    
    # Preparar dados para tabela
    df_table = df.head(10)
    df_table['DATETIME'] = pd.to_datetime(df_table['TIMESTAMP'], unit='s').dt.strftime('%d/%m/%Y %H:%M')
    
    columns_to_show = ['DATETIME', 'UMIDADE_DHT', 'LDR_VALOR', 'RELAY_STATUS', 'NPK_OK', 'PH_OK']
    df_table = df_table[columns_to_show]
    
    return dash_table.DataTable(
        data=df_table.to_dict('records'),
        columns=[{"name": col, "id": col} for col in df_table.columns],
        style_cell={'textAlign': 'center'},
        style_header={'backgroundColor': '#1f4e79', 'color': 'white'},
        style_data_conditional=[
            {
                'if': {'filter_query': '{RELAY_STATUS} = 1'},
                'backgroundColor': '#d4edda',
                'color': 'black',
            }
        ]
    )

# Callback para sugestões
@app.callback(
    Output('sugestoes', 'children'),
    [Input('data-store', 'data')]
)
def update_sugestoes(data):
    if not data:
        return html.Div()
    
    df = pd.DataFrame(data)
    if df.empty:
        return html.Div()
    
    # Calcular métricas
    umidade_media = df['UMIDADE_DHT'].mean()
    taxa_irrigacao = (df['RELAY_STATUS'].sum() / len(df)) * 100
    
    sugestoes = []
    
    if umidade_media < 45:
        sugestoes.append("⚠️ Umidade média baixa. Considere aumentar irrigação.")
    elif umidade_media > 75:
        sugestoes.append("✅ Umidade adequada. Sistema funcionando bem.")
    
    if taxa_irrigacao > 30:
        sugestoes.append("🔍 Alta ativação da irrigação. Verifique possíveis vazamentos.")
    elif taxa_irrigacao < 10:
        sugestoes.append("👍 Sistema de irrigação eficiente.")
    
    return html.Div([
        html.H3("🤖 Sugestões Inteligentes"),
        html.Ul([html.Li(sug) for sug in sugestoes])
    ])

# CSS inline
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body { font-family: Arial, sans-serif; margin: 0; background-color: #f5f5f5; }
            .header { background: linear-gradient(90deg, #1f4e79 0%, #2e7d4a 100%); color: white; padding: 20px; text-align: center; }
            .header-title { margin: 0; font-size: 2em; }
            .header-subtitle { margin: 5px 0 0 0; opacity: 0.9; }
            .controls { padding: 20px; background: white; margin: 10px; border-radius: 8px; }
            .metrics-container { display: flex; gap: 20px; margin: 20px; }
            .metric-card { background: white; padding: 20px; border-radius: 8px; flex: 1; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric-card h4 { margin: 0; font-size: 1.5em; color: #1f4e79; }
            .metric-card p { margin: 10px 0 0 0; color: #666; }
            .charts-row { display: flex; gap: 20px; margin: 20px; }
            .chart-container { flex: 1; background: white; padding: 20px; border-radius: 8px; }
            .table-container { margin: 20px; background: white; padding: 20px; border-radius: 8px; }
            .suggestions { margin: 20px; background: white; padding: 20px; border-radius: 8px; }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    print("🌱 Iniciando Dashboard de Irrigação Inteligente...")
    print("📊 Acesse: http://localhost:8050")
    app.run(debug=True, port=8050)