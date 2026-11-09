
#include "sensores/SensorLM35.h"

SensorLM35::SensorLM35(uint8_t pino, float peso, float intercept, uint16_t quantidade_amostras)
    : pino(pino),
    quantidade_amostras(quantidade_amostras),
    peso(peso),
    intercept(intercept)
{}

void SensorLM35::iniciar() {

    pinMode(pino, INPUT);
    analogRead(pino); //só para eliminar a primeira leitura não confiavel
}

float SensorLM35::ler_media() const {
    unsigned long soma = 0;

    for (uint16_t i = 0; i < quantidade_amostras; i++) {
        soma += analogRead(pino);
        delay(2);
    }

    return static_cast<float>(soma) / quantidade_amostras;
}

Temperatura SensorLM35::ler_temperatura() const {
    float tensao = ler_media() * 1.1f / 1023.0f;   // volts (referencia de 1,1 V)
    float leitura = tensao * 100.0f;               // LM35: 10 mV por grau C

    Temperatura t;
    t.celsius = peso * leitura + intercept;
    t.fahrenheit = t.celsius * 9.0f / 5.0f + 32.0f;
    return t;
}
