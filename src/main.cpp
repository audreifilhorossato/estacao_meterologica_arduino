#include <Arduino.h>
#include "sistema/EstacaoMeteorologica.h"

constexpr float PESO_LM35 = 0.048419f;
constexpr float INTERCEPT_LM35 = -0.0074385f;

constexpr float PESO_BMP280 = 1.0;
constexpr float INTERCEPT_BMP280 = 0.0;

constexpr float PESO_LDR5 = -2.361738;
constexpr float INTERCEPT_LDR5 = 9.97262783;

// DHT22 desativado para testes
// constexpr float PESO_DHT22 = 1.305f;
// constexpr float INTERCEPT_DHT22 = -16.6280f;


EstacaoMeteorologica estacao(
    A1,                  // LM35 (temperatura)
    PESO_LM35,           // LM35
    INTERCEPT_LM35,      // LM35
    0x76,                // BMP280 (I2C: SDA=A4, SCL=A5)
    PESO_BMP280,         // BMP280
    INTERCEPT_BMP280,    // BMP280
    A0,                  // LDR5 (luminosidade)
    PESO_LDR5,           // LDR5
    INTERCEPT_LDR5,      // LDR5
    // A1,                  // DHT22 (desativado)
    // PESO_DHT22,          // DHT22 (desativado)
    // INTERCEPT_DHT22,     // DHT22 (desativado)
    20                   // n de amostras
);

void setup() {
    estacao.iniciar();
}

void loop() {
    estacao.executar();
}