import serial
import os
import sys
import time
# Adicionar pyserial ao seu ambiente: pip install pyserial

# --- CONFIGURAÇÃO ---
SERIAL_PORT_URL = "rfc2217://localhost:4000"
BAUDRATE = 115200
OUTPUT_FILE = "r_analysis/esp32_log_bruto.csv"
CSV_HEADER = "Timestamp,Umidade,LDR_Valor,N_Botao,P_Botao,K_Botao,pH_Ideal,Umidade_Baixa,NPK_OK,Relay_Status,Bloqueio_Externo"


# Se o script receber um argumento, usa ele como número de linhas, senão usa 30.
NUM_LINES_TO_CAPTURE = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 30
# --- FIM CONFIGURAÇÃO ---

def capturar_log_serial():
    """Conecta e captura N linhas CSV do ESP32 simulado."""
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    print(f"Conectando ao Wokwi Serial Remoto em: {SERIAL_PORT_URL}")

    try:
        ser = serial.serial_for_url(SERIAL_PORT_URL, baudrate=BAUDRATE, timeout=5)
        ser.reset_input_buffer()
        time.sleep(3)  # Aguarda estabilização da conexão
        
        captured_lines = 0
        with open(OUTPUT_FILE, 'w') as f:
            
            # --- INSERE O CABEÇALHO AQUI ---
            f.write(CSV_HEADER + '\n')
            print(f"[Log] Cabeçalho inserido no arquivo.")
            # ------------------------------------
            
            # Pula as primeiras linhas que podem ser logs de debug (se o ESP32 enviar algo antes do loop)
            while True:
                line_test = ser.read_until(b'\n').decode('utf-8').strip()
                if line_test and line_test[0].isdigit():
                    # Encontrou a primeira linha de dados!
                    f.write(line_test + '\n')
                    captured_lines += 1
                    print(f"Linha {captured_lines}/{NUM_LINES_TO_CAPTURE}: {line_test}")
                    break
                
                # Previne loop infinito se não houver dados
                if captured_lines >= NUM_LINES_TO_CAPTURE:
                    break


            # Inicia a captura das linhas restantes
            while captured_lines < NUM_LINES_TO_CAPTURE:
                line_bytes = ser.read_until(b'\n')
                
                if line_bytes:
                    line = line_bytes.decode('utf-8').strip()
                    
                    # Garante que estamos escrevendo apenas linhas que se parecem com dados
                    if line and line[0].isdigit():
                        f.write(line + '\n')
                        captured_lines += 1
                        print(f"Linha {captured_lines}/{NUM_LINES_TO_CAPTURE}: {line}")
                        
        ser.close()
        print(f"\nCaptura finalizada. {captured_lines} linhas salvas em: {OUTPUT_FILE}")
        return 0

    except serial.SerialException as e:
        print(f"\n[ERRO FATAL] Falha de conexão serial. Detalhe: {e}")
        return 1
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit(capturar_log_serial())