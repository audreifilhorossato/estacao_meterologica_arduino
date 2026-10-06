#include <Arduino.h>
#include "sistema/EstacaoMeteorologica.h"

constexpr float PESO_LM35 = 0.048419f;
constexpr float INTERCEPT_LM35 = -0.0074385f;

constexpr float PESO_BMP280 = 1.0;
constexpr float INTERCEPT_BMP280 = 0.0;

constexpr float PESO_LDR5 = -2.361738;
constexpr float INTERCEPT_LDR5 = 9.97262783;

//constexpr float PESO_LDR5 = 1.0;
//constexpr float INTERCEPT_LDR5 = 0.0;

EstacaoMeteorologica estacao(
    A0,                  // LM35
    PESO_LM35,           // LM35
    INTERCEPT_LM35,      // LM35
    0x76,                // BMP280
    PESO_BMP280,         // BMP280
    INTERCEPT_BMP280,    // BMP280
    A2,                  // LDR5
    PESO_LDR5,           // LDR5
    INTERCEPT_LDR5,      // LDR5
    20,                  // n de amostras
    1000                 // intervalo
);

void setup() {
    estacao.iniciar();
}

void loop() {
    estacao.executar();
}