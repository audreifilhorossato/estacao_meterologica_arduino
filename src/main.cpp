#include <Arduino.h>
#include "sistema/EstacaoMeteorologica.h"

constexpr float PESO_LM35 = 1.0;
constexpr float INTERCEPT_LM35 = 0.0;

constexpr float PESO_BMP280 = 1.0;
constexpr float INTERCEPT_BMP280 = 0.0;

constexpr float PESO_LDR5 = -2.0;
constexpr float INTERCEPT_LDR5 = 9.0;

constexpr float PESO_DHT22 = 1.0;
constexpr float INTERCEPT_DHT22 = 0.0;

EstacaoMeteorologica estacao(
    A1,                  // LM35
    PESO_LM35,           // LM35
    INTERCEPT_LM35,      // LM35
    0x76,                // BMP280
    PESO_BMP280,         // BMP280
    INTERCEPT_BMP280,    // BMP280
    A0,                  // LDR5
    PESO_LDR5,           // LDR5
    INTERCEPT_LDR5,      // LDR5
    3,                   // DHT22
    PESO_DHT22,          // DHT22
    INTERCEPT_DHT22,     // DHT22
    20                   // n de amostras
);

void setup() {
    estacao.iniciar();
}

void loop() {
    estacao.executar();
}