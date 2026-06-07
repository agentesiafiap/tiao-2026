import pandas as pd
import os

# --- 1. Definições de Arquivo ---
INPUT_FILE = "r_analysis/esp32_log_bruto.csv"
OUTPUT_FILE = "r_analysis/dados_para_r.csv"

def processar_dados_para_r():
    try:
        print(f"Lendo dados brutos em: {INPUT_FILE}")
        
        # Leitura robusta, pulando linhas de log/debug que não são CSV
        df = pd.read_csv(INPUT_FILE, 
                          sep=',', 
                          skipinitialspace=True,
                          on_bad_lines='skip',
                          header=0) 
        
        # --- CORREÇÃO AQUI: Substituir 'LDR_pH' por 'LDR_Valor' ---
        # Note que a coluna 'Umidade' é 'Umidade' no cabeçalho.
        
        colunas_para_selecionar = [
            'Timestamp', 
            'Umidade', 
            'LDR_Valor', # NOME CORRETO
            'N_Botao', 
            'P_Botao', 
            'K_Botao', 
            'Relay_Status', 
            'Bloqueio_Externo'
        ]
        
        df_final = df[colunas_para_selecionar].copy()
        
        # Renomeia as colunas para um padrão mais amigável em R
        df_final.columns = ['Timestamp_ms', 'Umidade_DHT', 'Valor_LDR', 'N_Presente', 
                            'P_Presente', 'K_Presente', 'Bomba_Ligada', 'Bloqueio_Externo']
        
        # Adicionar feature de Data Science: Indice NPK Total
        df_final['Indice_NPK'] = df_final['N_Presente'] + df_final['P_Presente'] + df_final['K_Presente']

        # Exportação Final
        df_final.to_csv(OUTPUT_FILE, index=False)
        print(f"Sucesso! Arquivo CSV final para R criado em: {OUTPUT_FILE}")
        return 0

    except FileNotFoundError:
        print(f"ERRO: O arquivo de log bruto '{INPUT_FILE}' não foi encontrado. Execute a captura primeiro.")
        return 1
    except KeyError as e: 
        print(f"ERRO: Uma coluna esperada não foi encontrada no log bruto. Verifique a ortografia do cabeçalho. Detalhes: {e}")
        return 1
    except Exception as e:
        print(f"Ocorreu um erro durante o processamento: {e}")
        return 1

if __name__ == "__main__":
    exit(processar_dados_para_r())