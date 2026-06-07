import streamlit as st
import pandas as pd
from math import pi
import subprocess
import os
import joblib
import boto3
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import cv2
import shutil
import numpy as np
import oracledb

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from PIL import Image
try:
    from ultralytics import YOLO
except ImportError:
    pass 
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------
# CONFIGURAÇÕES INICIAIS E CAMINHOS DE ARQUIVOS
# ---------------------------------------------------------
st.set_page_config(page_title="FarmTech Solutions - Hub", layout="wide")

# Atualização dos caminhos apontando para a pasta 'data' e 'scripts'
ARQUIVO_DADOS = os.path.join("data", "dados_farmtech.csv")

if 'dados' not in st.session_state:
    if os.path.exists(ARQUIVO_DADOS):
        st.session_state.dados = pd.read_csv(ARQUIVO_DADOS)
    else:
        st.session_state.dados = pd.DataFrame(columns=['cultura','area_m2'])

# Função global para mensageria AWS
def enviar_alerta_aws(mensagem, assunto="Alerta FarmTech"):
    try:
        sns_client = boto3.client('sns', region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-2"))
        TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")
        
        response = sns_client.publish(
            TopicArn=TOPIC_ARN, 
            Message=mensagem, 
            Subject=assunto
        )
        return True, response['MessageId']
    except Exception as e:
        return False, str(e)

# ---------------------------------------------------------
# MENU ESTRUTURAL
# ---------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2874/2874058.png", width=100)
st.sidebar.title("Módulos")
menu = st.sidebar.radio(
    "Navegação do Sistema:",
    [
        "1. Cadastro e Áreas (F1)", 
        "2. Estatística e Clima (F1)", 
        "3. Monitoramento IoT e BD (F2/F3)", 
        "4. Predição de Safra ML (F4)", 
        "5. Visão Computacional (F6)",
        "6. Configurações AWS (F5)"
    ]
)

st.title("🌱 FarmTech Solutions - Hub Central (Fase 7)")

# ---------------------------------------------------------
# MÓDULO 1: CADASTRO DE CULTURAS (FASE 1)
# ---------------------------------------------------------
if menu == "1. Cadastro e Áreas (F1)":
    st.header("📝 Gestão de Talhões")
    
    # O seletor fica FORA do form para a tela mudar dinamicamente as medidas pedidas
    cultura = st.selectbox("Selecione o Tipo de Cultura:", ["Milho", "Soja"])
    
    with st.form("form_cultura"):
        # Interface exata conforme a lógica matemática do farmtech.py
        if cultura == "Milho":
            st.write("🌾 **Milho** (Cálculo de Área Retangular)")
            col1, col2 = st.columns(2)
            with col1:
                largura = st.number_input("Largura em metros:", min_value=0.0, format="%.2f")
            with col2:
                comprimento = st.number_input("Comprimento em metros:", min_value=0.0, format="%.2f")
        else:
            st.write("🌱 **Soja** (Cálculo de Área Circular - Pivô Central)")
            raio = st.number_input("Raio em metros:", min_value=0.0, format="%.2f")
            
        if st.form_submit_button("Registrar Área"):
            # Lógica matemática herdada da Fase 1
            if cultura == "Milho":
                area = largura * comprimento
            else:
                area = pi * (raio ** 2)
                
            nova_linha = pd.DataFrame([{'cultura': cultura.lower(), 'area_m2': area}])
            
            # Adiciona os dados e salva o CSV
            st.session_state.dados = pd.concat([st.session_state.dados, nova_linha], ignore_index=True)
            st.session_state.dados.to_csv(ARQUIVO_DADOS, index=False)
            
            st.success(f"Área cadastrada com sucesso: {area:.2f} m² e salva em {ARQUIVO_DADOS}")

    st.subheader("Base de Dados Atual")
    st.dataframe(st.session_state.dados, width='stretch')

# ---------------------------------------------------------
# MÓDULO 2: ESTATÍSTICA E CLIMA COM R (FASE 1)
# ---------------------------------------------------------
elif menu == "2. Estatística e Clima (F1)":
    st.header("📊 Análises via RScript")
    
    # Verifica se o R está instalado e disponível no PATH do sistema
    if shutil.which("Rscript") is None:
        st.error("🚨 **O R não foi encontrado neste computador!**")
        st.warning("Para utilizar este módulo, é necessário instalar o R base. Certifique-se também de que o 'Rscript' está adicionado às variáveis de ambiente (PATH) do seu sistema operativo.")
    else:
        st.success("✅ Motor do R detetado com sucesso. Pronto para executar análises.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Executar Estatística de Áreas (R)"):
                with st.spinner("A processar estatísticas no R..."):
                    res = subprocess.run(['Rscript', os.path.join('scripts', 'analise_estatistica.R')], capture_output=True, text=True)
                    st.code(res.stdout if res.returncode == 0 else res.stderr)
                
        with col2:
            if st.button("Consultar API Open-Meteo (R)"):
                with st.spinner("A consultar dados meteorológicos..."):
                    res = subprocess.run(['Rscript', os.path.join('scripts', 'analise_openmeteo.R')], capture_output=True, text=True)
                    st.code(res.stdout if res.returncode == 0 else res.stderr)

# ---------------------------------------------------------
# MÓDULO 3: MONITORAMENTO IOT E BANCO ORACLE (FASE 2 E 3)
# ---------------------------------------------------------
elif menu == "3. Monitoramento IoT e BD (F2/F3)":
    st.header("🎛️ Telemetria ESP32 e Conexão de Banco")
    
    aba1, aba2 = st.tabs(["Oracle Database", "Logs Brutos ESP32"])
    
    with aba1:
        st.write("Gestão e Consulta ao banco relacional estruturado na Fase 3.")
        
        # 1. Cria um estado na memória para guardar as credenciais de forma dinâmica
        if 'oracle_creds' not in st.session_state:
            st.session_state.oracle_creds = {
                'user': os.getenv("DB_USER", ""),
                'pass': os.getenv("DB_PASS", ""),
                'host': os.getenv("DB_HOST", ""),
                'port': os.getenv("DB_PORT", "1521"),
                'service': os.getenv("DB_SERVICE", "")
            }

        # =========================================================
        # SESSÃO: ÁREA DO ADMINISTRADOR
        # =========================================================
        with st.expander("🛠️ Acesso Administrativo: Criar Tabela e Importar CSV"):
            st.write("Insira as credenciais para recriar a tabela `DADO_AGRICOLA` e popular com os dados históricos.")
            
            with st.form("form_admin_oracle"):
                col1, col2 = st.columns(2)
                with col1:
                    # Agora os campos puxam da memória (se o .env funcionar, já vem preenchido)
                    admin_user = st.text_input("Usuário do Banco:", value=st.session_state.oracle_creds['user'])
                    admin_host = st.text_input("Host (ex: oracle.fiap.com.br):", value=st.session_state.oracle_creds['host'])
                    admin_service = st.text_input("Service Name (ex: ORCL):", value=st.session_state.oracle_creds['service'])
                with col2:
                    admin_pass = st.text_input("Senha:", value=st.session_state.oracle_creds['pass'], type="password")
                    admin_port = st.text_input("Porta:", value=st.session_state.oracle_creds['port'])
                    
                submit_import = st.form_submit_button("Criar Tabela e Injetar Dados")
                
                if submit_import:
                    if not admin_user or not admin_pass or not admin_host or not admin_service:
                        st.error("Por favor, preencha todas as credenciais administrativas.")
                    else:
                        with st.spinner("Conectando ao Oracle e processando os dados..."):
                            try:
                                caminho_csv = os.path.join('data', 'dados_historicos_2024.csv')
                                df_import = pd.read_csv(caminho_csv)
                                df_import = df_import.where(pd.notnull(df_import), None)
                                
                                conn_admin = oracledb.connect(
                                    user=admin_user, password=admin_pass, 
                                    host=admin_host, port=admin_port, service_name=admin_service
                                )
                                cursor = conn_admin.cursor()
                                
                                try:
                                    cursor.execute("DROP TABLE DADO_AGRICOLA")
                                except oracledb.DatabaseError:
                                    pass 
                                    
                                sql_create = """
                                CREATE TABLE DADO_AGRICOLA (
                                    ID NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                                    TIMESTAMP NUMBER,
                                    UMIDADE_DHT NUMBER(5,2),
                                    LDR_VALOR NUMBER(5,0),
                                    N_PRESENTE NUMBER(1,0),
                                    P_PRESENTE NUMBER(1,0),
                                    K_PRESENTE NUMBER(1,0),
                                    BLOQUEIO_EXTERNO NUMBER(1,0),
                                    RELAY_STATUS NUMBER(1,0),
                                    UMIDADE_BAIXA NUMBER(1,0),
                                    NPK_OK NUMBER(1,0),
                                    PH_OK NUMBER(1,0)
                                )
                                """
                                cursor.execute(sql_create)
                                
                                dados_tuplas = [tuple(x) for x in df_import.values]
                                
                                sql_insert = """
                                INSERT INTO DADO_AGRICOLA (
                                    TIMESTAMP, UMIDADE_DHT, LDR_VALOR, N_PRESENTE, P_PRESENTE, K_PRESENTE, BLOQUEIO_EXTERNO, RELAY_STATUS, UMIDADE_BAIXA, NPK_OK, PH_OK
                                ) VALUES (:2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12)
                                """

                                cursor.executemany(sql_insert, dados_tuplas)
                                conn_admin.commit()
                                conn_admin.close()
                                
                                # Salvamos as credenciais que deram certo na "memória" do sistema
                                st.session_state.oracle_creds = {
                                    'user': admin_user,
                                    'pass': admin_pass,
                                    'host': admin_host,
                                    'port': admin_port,
                                    'service': admin_service
                                }
                                
                                st.success(f"Sucesso! {len(df_import)} linhas importadas.")
                                
                            except FileNotFoundError:
                                st.error(f"O arquivo CSV não foi encontrado.")
                            except Exception as e:
                                st.error(f"Erro durante a operação no banco: {e}")

        # =========================================================
        # SESSÃO DE LEITURA (Agora conectada à memória)
        # =========================================================
        st.divider()
        st.subheader("Visualização dos Dados (Leitura)")
        try:
        # Puxa as credenciais direto da memória (st.session_state)
            db_c = st.session_state.oracle_creds

        # Se não houver usuário, pede para preencher em vez de estourar erro
            if not db_c['user'] or not db_c['pass']:
                st.info("👈 Por favor, insira suas credenciais na aba administrativa acima para visualizar os dados.")
            else:
                conn = oracledb.connect(
                    user=db_c['user'], password=db_c['pass'], 
                    host=db_c['host'], port=db_c['port'], service_name=db_c['service']
                )
                
                query = """
                SELECT 
                    TIMESTAMP, UMIDADE_DHT, LDR_VALOR, N_PRESENTE, P_PRESENTE, K_PRESENTE, BLOQUEIO_EXTERNO, RELAY_STATUS, UMIDADE_BAIXA, NPK_OK, PH_OK 
                FROM DADO_AGRICOLA 
                ORDER BY id DESC 
                FETCH FIRST 50 ROWS ONLY
                """
                
                df_oracle = pd.read_sql(query, conn)
                conn.close()
                
                st.dataframe(df_oracle, width='stretch')

        except Exception as e:
            st.warning("Não foi possível carregar os dados. Verifique as credenciais ou se a tabela já foi criada.")
            st.info(f"Detalhe técnico: {e}")
            
    with aba2:
        st.write("Leitura dos logs físicos e dados históricos do hardware IoT.")
        try:
            caminho_historico = os.path.join('data', 'dados_historicos_2024.csv')
            
            # Lê o arquivo normalmente identificando o cabeçalho existente
            df_logs = pd.read_csv(caminho_historico)
            
            # Exibe as 20 últimas leituras no painel
            st.dataframe(df_logs.tail(20), width='stretch')
            
            # Lógica dinâmica para encontrar as colunas corretas para o gráfico
            # Procura por qualquer coluna que contenha 'umid' ou 'ph' no nome
            col_umidade = [c for c in df_logs.columns if 'umid' in c.lower()]
            col_ph = [c for c in df_logs.columns if 'ph' in c.lower()]
            
            # Se encontrar as colunas no arquivo, plota o gráfico
            if col_umidade and col_ph:
                st.line_chart(df_logs[[col_umidade[0], col_ph[0]]])
            else:
                st.warning(f"Atenção: O gráfico precisa de colunas de umidade e ph. Colunas encontradas no seu arquivo: {list(df_logs.columns)}")
            
        except FileNotFoundError:
            st.info(f"Arquivo '{caminho_historico}' não encontrado. Verifique se ele está na pasta 'data/'.")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")

# ---------------------------------------------------------
# MÓDULO 4: PREDIÇÃO DE SAFRA (FASE 4)
# ---------------------------------------------------------
elif menu == "4. Predição de Safra ML (F4)":
    st.header("🤖 Machine Learning (Scikit-Learn)")
           
    # Dividindo o módulo nas duas entregas da Fase 4
    aba_pred,aba_eda = st.tabs(["🎯 Predição e Recomendações","📊 Análise Exploratória e Clusters"])
        
    # ==========================================
    # ABA 1: A CALCULADORA PREDITIVA
    # ==========================================
    
    with aba_pred:
        st.write("Utilize o modelo de Regressão treinado para obter sugestões de manejo.")
        try:
            from scripts import recommend 
            
            col1, col2, col3 = st.columns(3)
            with col1: 
                soil_moisture = st.number_input("Umidade do Solo (%)", min_value=0.0, max_value=100.0, value=25.0)
                air_temp = st.number_input("Temperatura do Ar (°C)", min_value=-10.0, max_value=60.0, value=24.0)
            with col2: 
                soil_ph = st.number_input("pH do Solo", min_value=0.0, max_value=14.0, value=6.2)
                humidity = st.number_input("Umidade Relativa do Ar (%)", min_value=0.0, max_value=100.0, value=60.0)
            with col3:
                irrigation_ml = st.number_input("Irrigação Aplicada (mL)", min_value=0.0, value=0.0)
                fertilizer_kg = st.number_input("Fertilizante Aplicado (kg)", min_value=0.0, value=0.0)
                
            if st.button("Executar Predição e Gerar Recomendações"):
                with st.spinner("Processando dados com o modelo..."):
                    features_extras = {
                        "air_temp": air_temp,
                        "humidity": humidity,
                        "irrigation_ml": irrigation_ml,
                        "fertilizer_kg": fertilizer_kg
                    }
                    
                    resultado = recommend.recommend_from_point(
                        soil_moisture=soil_moisture, 
                        soil_ph=soil_ph, 
                        features=features_extras
                    )
                    
                st.divider()
                st.subheader("📊 Resultados da Análise")
                st.metric(label="Rendimento Previsto (Yield)", value=f"{resultado['predicted_yield']:.4f} ton/ha")
                
                st.markdown("### 💡 Plano de Ação Sugerido")
                st.info(f"**💧 Irrigação:** {resultado['irrigation_ml_suggested']} mL\n\n**Motivo:** {resultado['irrigation_reason']}")
                st.success(f"**🧪 Fertilizante:** {resultado['fertilizer_kg_suggested']} kg\n\n**Motivo:** {resultado['fertilizer_reason']}")
                
                if resultado['predicted_yield'] < 0.06 or resultado['irrigation_ml_suggested'] > 0:
                    st.warning("⚠️ Gatilho de alerta acionado. Enviando notificação via AWS SNS...")
                    msg_alerta = f"ALERTA FARMTECH: Rendimento estimado: {resultado['predicted_yield']:.4f} ton/ha. Recomendado aplicar {resultado['irrigation_ml_suggested']} mL de água."
                    sucesso, log = enviar_alerta_aws(msg_alerta)
                    if sucesso:
                        st.toast(f"Alerta enviado à equipe física! (ID: {log})")
                        
        except ImportError as e:
            st.error(f"Erro ao importar módulo de recomendação. Detalhes: {e}")
        except Exception as e:
            st.error(f"Erro na predição: {e}")

    # ==========================================
    # ABA 2: O NOTEBOOK DE VOCÊS TRADUZIDO
    # ==========================================
    with aba_eda:
        st.write("Análise de padrões climáticos, clusterização e detecção de outliers na base histórica de safras.")
            
        try:
            caminho_crop = os.path.join('data', 'crop_yield.csv')
            df_crop = pd.read_csv(caminho_crop)
            
            st.subheader("1. Distribuição e Rendimento por Cultura")
            sns.set_theme(style="whitegrid")
            fig1, ax1 = plt.subplots(1, 2, figsize=(14, 5))
            
            sns.histplot(df_crop['Yield'], kde=True, ax=ax1[0])
            ax1[0].set_title('Distribuição de Rendimento (Yield)')
            
            sns.boxplot(x='Crop', y='Yield', data=df_crop, ax=ax1[1])
            ax1[1].set_title('Rendimento por Cultura')
            ax1[1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            st.pyplot(fig1)
            
            st.subheader("2. Matriz de Correlação")
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            corr = df_crop.select_dtypes(include=['float64', 'int64']).corr()
            sns.heatmap(corr, annot=True, cmap='YlGnBu', fmt=".2f", ax=ax2)
            ax2.set_title('Correlação de Variáveis')
            st.pyplot(fig2)
            
            st.subheader("3. Clusterização (K-Means e PCA)")
            with st.spinner("Calculando clusters dinamicamente..."):
                df_unsup = df_crop.copy()
                le = LabelEncoder()
                if 'Crop' in df_unsup.columns:
                    df_unsup['Crop_encoded'] = le.fit_transform(df_unsup['Crop'])
                    X_cluster = df_unsup.drop(['Crop', 'Yield'], axis=1, errors='ignore')
                else:
                    X_cluster = df_unsup.drop(['Yield'], axis=1, errors='ignore')
                
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X_cluster)
                
                kmeans = KMeans(n_clusters=3, random_state=42) # Usando k=3 para agilizar no painel
                df_unsup['Cluster_KMeans'] = kmeans.fit_predict(X_scaled)
                
                pca = PCA(n_components=2)
                X_pca = pca.fit_transform(X_scaled)
                df_unsup['PCA1'] = X_pca[:, 0]
                df_unsup['PCA2'] = X_pca[:, 1]
                
                fig3, ax3 = plt.subplots(figsize=(8, 6))
                sns.scatterplot(x='PCA1', y='PCA2', hue='Cluster_KMeans', data=df_unsup, palette='viridis', ax=ax3)
                ax3.set_title('Visualização dos Clusters (PCA 2D)')
                st.pyplot(fig3)
                
                # DBSCAN Outliers
                dbscan = DBSCAN(eps=1.5, min_samples=5)
                outliers = (dbscan.fit_predict(X_scaled) == -1).sum()
                st.info(f"🔍 **DBSCAN:** Foram detectados **{outliers} outliers** na base histórica.")
                
        except FileNotFoundError:
            st.error("Arquivo 'crop_yield.csv' não encontrado na pasta 'data/'.")
        except Exception as e:
            st.error(f"Erro ao gerar gráficos: {e}")



# ---------------------------------------------------------
# MÓDULO 5: VISÃO COMPUTACIONAL (FASE 6)
# ---------------------------------------------------------
elif menu == "5. Visão Computacional (F6)":
    st.header("👁️ YOLOv5: Diagnóstico Especializado e Segurança")
    
    st.write("Prova de Conceito (PoC) FarmTech focada em duas verticais de alto valor:")
    st.markdown("""
    * 🐶 **Saúde Animal:** Monitoramento clínico e pós-operatório (Alvo: *Shih Tzu*).
    * 🚙 **Segurança Patrimonial:** Controle de acesso inteligente (Alvo: *Nissan Kicks*).
    """)
    
    # === OTIMIZAÇÃO: Cache do Modelo ===
    # O Streamlit guarda o modelo na memória para não o carregar 2 vezes
    @st.cache_resource(show_spinner=False)
    def carregar_modelo_yolo():
        # Alterado force_reload para False para não baixar da internet a cada clique
        return torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5_farmtech.pt', force_reload=False, trust_repo=True)
    
    aba_inferencia, aba_metricas = st.tabs(["🔍 Análise de Imagem (PoC)", "📈 Métricas do Modelo (60 Épocas)"])
    
    # --- ABA DE INFERÊNCIA ---
    with aba_inferencia:
        st.write("Faça o upload de uma imagem do paciente veterinário ou da câmera de segurança.")
        
        img_upload = st.file_uploader("Envie a imagem (jpg, png, jpeg)", type=["jpg", "png", "jpeg"])
        
        if img_upload:
            imagem_pil = Image.open(img_upload).convert('RGB')
            
            st.image(imagem_pil, caption="Câmera / Imagem Original", use_container_width=True)
            
            if st.button("Executar Diagnóstico YOLOv5"):
                with st.spinner("Processando a imagem através da Rede Neural..."):
                    try:
                        modelo_yolov5 = carregar_modelo_yolo()
                        
                        img_cv = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)
                        
                        resultados = modelo_yolov5(img_cv)
                        
                        resultados.render()
                        img_processada = cv2.cvtColor(resultados.ims[0], cv2.COLOR_BGR2RGB)
                        
                        st.divider()
                        st.subheader("Resultado da Detecção")
                        st.image(img_processada, caption="Análise Concluída", use_container_width=True)
                        
                        df_deteccoes = resultados.pandas().xyxy[0]
                        
                        if len(df_deteccoes) > 0:
                            st.success(f"✅ Análise concluída. {len(df_deteccoes)} objeto(s) alvo(s) identificado(s).")
                            st.dataframe(df_deteccoes[['name', 'confidence']])
                            
                            classes_detectadas = df_deteccoes['name'].str.lower().tolist()
                            mensagens_aws = []
                            
                            if any(c in ['shih tzu', 'shihtzu', 'dog', 'cachorro'] for c in classes_detectadas):
                                st.info("🐶 **Suporte Decisão Clínica:** Paciente (Shih Tzu) detectado.")
                                mensagens_aws.append("Saúde Animal: Monitoramento ativado no painel clínico.")
                                
                            if any(c in ['nissan kicks', 'kicks', 'car', 'carro', 'veiculo'] for c in classes_detectadas):
                                st.warning("🚙 **Controle de Acesso:** Veículo alvo (Nissan Kicks) reconhecido com sucesso.")
                                mensagens_aws.append("Segurança: Acesso liberado/registrado.")
                                
                            if mensagens_aws:
                                msg_final = " | ".join(mensagens_aws)
                                enviar_alerta_aws(f"ALERTA FARMTECH V.A.: {msg_final}")
                                st.toast("Notificação de evento enviada via AWS SNS.")
                                
                        else:
                            st.warning("Nenhum objeto alvo das verticais foi detectado na imagem.")
                            
                    except Exception as e:
                        st.error(f"Erro ao processar o modelo YOLOv5: {e}")
                        st.info("Consulte o terminal do VS Code para ver os detalhes do erro.")

    # --- ABA DE MÉTRICAS ---
    with aba_metricas:
        st.write("Desempenho do modelo treinado na nuvem.")
        col1, col2 = st.columns(2)
        try:
            with col1:
                st.image("data/confusion_matrix.png", caption="Matriz de Confusão", use_container_width=True)
            with col2:
                st.image("data/F1_curve.png", caption="Curva F1-Score", use_container_width=True)
        except FileNotFoundError:
            st.info("Para exibir as métricas, certifique-se de que salvou os ficheiros na pasta 'data/'.")

            
# ---------------------------------------------------------
# MÓDULO 6: CONFIGURAÇÕES AWS (FASE 5)
# ---------------------------------------------------------
elif menu == "6. Configurações AWS (F5)":
    st.header("☁️ Gestão de Mensageria Cloud")
    st.write("Disparo de notificações SNS para a equipe de campo.")
    
    txt = "Alerta de teste do sistema de consolidação FarmTech."
    msg_teste = st.text_area("Mensagem:", txt)
    if st.button("Testar Disparo SNS"):
        sucesso, log = enviar_alerta_aws(txt)
        if sucesso:
            st.success(f"Mensagem enviada com sucesso! ID: {log}")
        else:
            st.error(f"Falha na AWS. Erro: {log}")
