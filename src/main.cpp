#include <Arduino.h>
#include "sistema/EstacaoMeteorologica.h"

const float PESO_LM35 = 0.9908;
const float INTERCEPT_LM35 = -0.75;

const float PESO_LDR5 = -2.36173795;
const float INTERCEPT_LDR5 = 9.97262783;

const float PESO_DHT22 = 1.302407;
const float INTERCEPT_DHT22 = -17.013343;

EstacaoMeteorologica estacao(
    A1,                  // LM35
    PESO_LM35,           // LM35
    INTERCEPT_LM35,      // LM35
    0x76,                // BMP280
    A0,                  // LDR5
    PESO_LDR5,           // LDR5
    INTERCEPT_LDR5,      // LDR5
    9,                   // DHT22
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