// **Sistema de Irrigação Inteligente - FarmTech Solutions (Unificado)**
// Cultura: Café | Lógica: Completa + Bloqueio Externo | Saída: CSV

#include <DHT.h> 
#include <WiFi.h> // Mantido para compatibilidade PlatformIO

// Definição dos pinos
const int PIN_BTN_N = 32;      // Botão Nitrogênio
const int PIN_BTN_P = 14;      // Botão Fósforo
const int PIN_BTN_K = 13;      // Botão Potássio
const int PIN_SENSOR_PH = 34;  // Sensor pH (LDR)
const int PIN_DHT = 21;        // Sensor DHT22
const int PIN_BOMBA = 17;      // Relé da bomba d'água

// --- Configurações da Cultura (Café) ---
const float PH_MIN_IDEAL = 5.5; 
const float PH_MAX_IDEAL = 6.5; 
const float UMIDADE_LIMITE = 60.0;

// --- Variáveis de Estado (Mantidas do Colega) ---
bool estadoN = false;
bool estadoP = false;
bool estadoK = false;
bool lastBtnN = HIGH;
bool lastBtnP = HIGH;
bool lastBtnK = HIGH;

// Variável de Bloqueio Externo (0=OK, 1=Bloqueio por API/R)
int bloqueio_irrigacao = 0; 
char dado_serial;

// Configuração do sensor DHT22
#define DHTTYPE DHT22
DHT dht(PIN_DHT, DHTTYPE);

// Estrutura para armazenar os dados dos sensores
struct DadosSensores {
    bool nivelN;
    bool nivelP;
    bool nivelK;
    float valorLDR;
    float umidade;
};

// --- Setup ---
void setup() {
    Serial.begin(115200);
    
    // Configura os pinos
    pinMode(PIN_BTN_N, INPUT_PULLUP);
    pinMode(PIN_BTN_P, INPUT_PULLUP);
    pinMode(PIN_BTN_K, INPUT_PULLUP);
    pinMode(PIN_BOMBA, OUTPUT);
    digitalWrite(PIN_BOMBA, HIGH); // Inicia Desligado (HIGH)
    
    dht.begin();
}

// Função para ler o Serial Remoto (API/R-Analysis)
void lerStatusBloqueioSerial() {
  while (Serial.available()) {
    dado_serial = Serial.read();
    
    if (dado_serial == '1') {
      bloqueio_irrigacao = 1;
      Serial.println(">>> DADO EXTERNO RECEBIDO: BLOQUEIO ATIVADO <<<");
    } else if (dado_serial == '0') {
      bloqueio_irrigacao = 0;
      Serial.println(">>> DADO EXTERNO RECEBIDO: BLOQUEIO DESATIVADO <<<");
    }
  }
}

// Função para ler os sensores (mantendo a lógica de TOGGLE do colega)
DadosSensores lerSensores() {
    DadosSensores dados;
    
    // Lê os estados atuais dos botões (LOW quando pressionado)
    bool currentBtnN = digitalRead(PIN_BTN_N);
    bool currentBtnP = digitalRead(PIN_BTN_P);
    bool currentBtnK = digitalRead(PIN_BTN_K);
    
    // Lógica de TOGGLE (Inverte o estado do nutriente com um toque)
    if (currentBtnN == LOW && lastBtnN == HIGH) {
        estadoN = !estadoN;
    }
    lastBtnN = currentBtnN;
    
    if (currentBtnP == LOW && lastBtnP == HIGH) {
        estadoP = !estadoP;
    }
    lastBtnP = currentBtnP;
    
    if (currentBtnK == LOW && lastBtnK == HIGH) {
        estadoK = !estadoK;
    }
    lastBtnK = currentBtnK;
    
    // Atualiza os níveis
    dados.nivelN = estadoN;
    dados.nivelP = estadoP;
    dados.nivelK = estadoK;
    
    // Lê o sensor de pH (LDR) - Usamos o valor ADC bruto para a lógica
    int valorLDR = analogRead(PIN_SENSOR_PH);
    dados.valorLDR = (valorLDR * 14.0) / 4095.0;  // Converte para escala pH (0-14)
    
    // Lê umidade
    dados.umidade = dht.readHumidity();
    if (isnan(dados.umidade)) {
        dados.umidade = 100.0; // Valor seguro em caso de falha
    }
    
    return dados;
}

// Função para aplicar a Lógica de Decisão (Cultura do Café)
bool aplicarLogicaIrrigacao(const DadosSensores& dados, int bloqueio) {
    
    // Condição A: Umidade está Baixa (precisa irrigar?)
    bool umidade_baixa = (dados.umidade < UMIDADE_LIMITE);
    
    // Condição B: NPK está presente? (Café requer os 3)
    bool npk_ok = (dados.nivelN && dados.nivelP && dados.nivelK);
    
    // Condição C: pH está na faixa ideal? (LDR entre 1500-2500)
    bool ph_ideal = (dados.valorLDR >= PH_MIN_IDEAL && dados.valorLDR <= PH_MAX_IDEAL);

    // Condição D: Bloqueio Externo Ativo?
    bool irrigacao_bloqueada = (bloqueio == 1);
    
    // Regra Final: LIGA se (A E B E C) E (NÃO D)
    bool ligar_bomba = umidade_baixa && npk_ok && ph_ideal && !irrigacao_bloqueada;

    return ligar_bomba;
}

// Função para imprimir a saída em formato CSV (para Data Science)
void imprimirSaidaCSV(const DadosSensores& dados, bool ligar_bomba, bool npk_ok, bool umidade_baixa, bool ph_ideal) {
    
    // -----------------------------------------------------------------------------------
    // Saída no formato CSV: Timestamp,Umidade,LDR_Valor,N_Botao,P_Botao,K_Botao,pH_Ideal,Umidade_Baixa,NPK_OK,Relay_Status,Bloqueio_Externo
    // -----------------------------------------------------------------------------------
    Serial.print(millis()); Serial.print(",");
    Serial.print(dados.umidade); Serial.print(",");
    Serial.print(dados.valorLDR); Serial.print(",");
    
    // Níveis NPK (0 ou 1)
    Serial.print(dados.nivelN ? "1" : "0"); Serial.print(",");
    Serial.print(dados.nivelP ? "1" : "0"); Serial.print(",");
    Serial.print(dados.nivelK ? "1" : "0"); Serial.print(",");

    // Decisões Intermediárias (0 ou 1)
    Serial.print(ph_ideal ? "1" : "0"); Serial.print(",");
    Serial.print(umidade_baixa ? "1" : "0"); Serial.print(",");
    Serial.print(npk_ok ? "1" : "0"); Serial.print(",");

    // Status Final (0 ou 1)
    Serial.print(ligar_bomba ? "1" : "0"); Serial.print(",");
    Serial.print(bloqueio_irrigacao ? "1" : "0"); 
    
    // Finaliza a linha CSV
    Serial.println(); 
}


void loop() {
    // 1. Checa por bloqueio externo (API/R)
    lerStatusBloqueioSerial();

    // 2. Lê os dados dos sensores
    DadosSensores dados = lerSensores();
    
    // 3. Aplica a lógica de decisão
    bool ligar_bomba = aplicarLogicaIrrigacao(dados, bloqueio_irrigacao);
    
    // 4. Atuação: Atualiza o estado da bomba
    digitalWrite(PIN_BOMBA, ligar_bomba ? HIGH : LOW);
    
    // 5. Imprime o status em formato CSV
    // A função aplicarLogicaIrrigacao não retorna as variáveis intermediárias,
    // então as recalculamos aqui para o log (apenas NPK_OK, Umidade_Baixa, pH_Ideal):
    bool umidade_baixa = (dados.umidade < UMIDADE_LIMITE);
    bool npk_ok = (dados.nivelN && dados.nivelP && dados.nivelK);
    bool ph_ideal = (dados.valorLDR >= PH_MIN_IDEAL && dados.valorLDR <= PH_MAX_IDEAL);

    imprimirSaidaCSV(dados, ligar_bomba, npk_ok, umidade_baixa, ph_ideal);
    
    // Aguarda 5 segundos antes da próxima leitura (para o Data Science Pipeline)
    delay(5000);
}