/*
 * esp32_magnetometer.ino — HeliOS Estação Terrestre de Magnetometria
 * HeliOS | Global Solution 2026.1 — FIAP
 *
 * Hardware necessário:
 *   - ESP32 (qualquer variante com WiFi)
 *   - Sensor magnético QMC5883L ou HMC5883L (I2C, ~R$15)
 *   - Conexão: SDA → GPIO21, SCL → GPIO22
 *
 * O que este código faz:
 *   1. Conecta ao WiFi
 *   2. Conecta ao AWS IoT Core via MQTT/TLS (certificados mTLS)
 *   3. Lê campo magnético X, Y, Z do sensor a cada 30 segundos
 *   4. Publica JSON no tópico: helios/magnetometer
 *
 * Bibliotecas necessárias (Arduino Library Manager):
 *   - PubSubClient (Nick O'Leary)
 *   - ArduinoJson (Benoit Blanchon)
 *   - QMC5883LCompass (MPrograms) — ou Adafruit_HMC5883_Unified
 *
 * ATENÇÃO: Em ambiente Vocareum/Lab, o AWS IoT Core está bloqueado.
 * Use src/iot/simulate_esp32.py para simular este comportamento via Python.
 *
 * Configuração AWS IoT Core (ver iot_setup.sh):
 *   1. Criar Thing: helios-magnetometer-station
 *   2. Gerar certificado + chave privada
 *   3. Criar Policy com iot:Connect + iot:Publish
 *   4. Colar os certificados nas constantes abaixo
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
// #include <QMC5883LCompass.h>  // descomente se tiver o sensor físico

// ─── Credenciais WiFi ─────────────────────────────────────────────────────────
const char* WIFI_SSID     = "SEU_WIFI_SSID";
const char* WIFI_PASSWORD = "SUA_SENHA_WIFI";

// ─── AWS IoT Core ─────────────────────────────────────────────────────────────
const char* IOT_ENDPOINT  = "SEU_ENDPOINT.iot.us-east-1.amazonaws.com";
const char* IOT_TOPIC     = "helios/magnetometer";
const char* THING_NAME    = "helios-magnetometer-station";
const int   MQTT_PORT     = 8883;  // TLS

// ─── Certificados mTLS (gerados pelo iot_setup.sh) ────────────────────────────
// Cole aqui o conteúdo dos arquivos gerados por aws iot create-keys-and-certificate
const char* CA_CERT = R"EOF(
-----BEGIN CERTIFICATE-----
<COLE_AQUI_O_CONTEUDO_DE_AmazonRootCA1.pem>
-----END CERTIFICATE-----
)EOF";

const char* CLIENT_CERT = R"EOF(
-----BEGIN CERTIFICATE-----
<COLE_AQUI_O_CONTEUDO_DE_certificate.pem.crt>
-----END CERTIFICATE-----
)EOF";

const char* PRIVATE_KEY = R"EOF(
-----BEGIN RSA PRIVATE KEY-----
<COLE_AQUI_O_CONTEUDO_DE_private.pem.key>
-----END RSA PRIVATE KEY-----
)EOF";

// ─── Localização da estação ───────────────────────────────────────────────────
const char* DEVICE_ID  = "helios-station-BR-001";
const float LATITUDE   = -23.5505;  // São Paulo
const float LONGITUDE  = -46.6333;

const unsigned long PUBLISH_INTERVAL_MS = 30000;  // 30 segundos

// ─── Objetos globais ──────────────────────────────────────────────────────────
WiFiClientSecure wifiClient;
PubSubClient mqttClient(wifiClient);
// QMC5883LCompass compass;  // descomente se tiver o sensor físico

unsigned long lastPublish = 0;

// ─── Leitura do sensor (com fallback sintético) ───────────────────────────────
struct MagReading {
    float bx, by, bz, btotal;
};

MagReading readSensor() {
    MagReading r;

#ifdef USE_REAL_SENSOR
    // Com sensor físico:
    // compass.read();
    // r.bx = compass.getX();
    // r.by = compass.getY();
    // r.bz = compass.getZ();
#else
    // Simulação sintética (sem sensor físico)
    // Campo magnético base de São Paulo ~23.000 nT com variação
    float baseline = 23000.0;
    float noise    = (float)(random(-200, 200));
    r.bx = baseline * 0.82 + noise;
    r.by = baseline * 0.35 + (float)(random(-100, 100));
    r.bz = baseline * 0.45 + (float)(random(-150, 150));
#endif

    r.btotal = sqrt(r.bx * r.bx + r.by * r.by + r.bz * r.bz);
    return r;
}

// ─── Conexão WiFi ─────────────────────────────────────────────────────────────
void connectWiFi() {
    Serial.print("Conectando ao WiFi: ");
    Serial.println(WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi conectado. IP: " + WiFi.localIP().toString());
}

// ─── Conexão MQTT/TLS ─────────────────────────────────────────────────────────
void connectMQTT() {
    wifiClient.setCACert(CA_CERT);
    wifiClient.setCertificate(CLIENT_CERT);
    wifiClient.setPrivateKey(PRIVATE_KEY);
    mqttClient.setServer(IOT_ENDPOINT, MQTT_PORT);
    mqttClient.setBufferSize(512);

    Serial.print("Conectando ao AWS IoT Core...");
    while (!mqttClient.connected()) {
        if (mqttClient.connect(THING_NAME)) {
            Serial.println(" conectado!");
        } else {
            Serial.print(" falhou (rc=");
            Serial.print(mqttClient.state());
            Serial.println("). Tentando novamente em 5s...");
            delay(5000);
        }
    }
}

// ─── Publicar leitura ─────────────────────────────────────────────────────────
void publishReading() {
    MagReading mag = readSensor();

    // Classificação simplificada de distúrbio
    float delta = mag.btotal - 23000.0;
    const char* geoStatus;
    if      (delta > -100)   geoStatus = "QUIET";
    else if (delta > -500)   geoStatus = "ACTIVE";
    else if (delta > -2000)  geoStatus = "STORM_MINOR";
    else                     geoStatus = "STORM_MAJOR";

    // Montar JSON
    StaticJsonDocument<256> doc;
    doc["device_id"]   = DEVICE_ID;
    doc["latitude"]    = LATITUDE;
    doc["longitude"]   = LONGITUDE;
    doc["b_total_nT"]  = round(mag.btotal * 100) / 100.0;
    doc["b_x_nT"]      = round(mag.bx * 100) / 100.0;
    doc["b_y_nT"]      = round(mag.by * 100) / 100.0;
    doc["b_z_nT"]      = round(mag.bz * 100) / 100.0;
    doc["geo_status"]  = geoStatus;

    char payload[256];
    serializeJson(doc, payload);

    if (mqttClient.publish(IOT_TOPIC, payload)) {
        Serial.print("Publicado: ");
        Serial.println(payload);
    } else {
        Serial.println("Falha ao publicar!");
    }
}

// ─── Setup e Loop ─────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    randomSeed(analogRead(0));

    // compass.init();  // descomente se tiver o sensor físico

    connectWiFi();
    connectMQTT();
    publishReading();  // primeira leitura imediata
    lastPublish = millis();
}

void loop() {
    if (!mqttClient.connected()) {
        connectMQTT();
    }
    mqttClient.loop();

    if (millis() - lastPublish >= PUBLISH_INTERVAL_MS) {
        publishReading();
        lastPublish = millis();
    }
}
