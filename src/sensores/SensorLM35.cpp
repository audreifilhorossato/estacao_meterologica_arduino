
#include "sensores/SensorLM35.h"

SensorLM35::SensorLM35(int pino, float peso, float intercept, int quantidade_amostras)
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
    long soma = 0; // long: 20 leituras x 1023 quase estoura o int (máx. 32767)

    for (int i = 0; i < quantidade_amostras; i++) {
        soma += analogRead(pino);
        delay(2);
    }

    return static_cast<float>(soma) / quantidade_amostras;
}

Temperatura SensorLM35::ler_temperatura() const {
    float tensao = ler_media() * 1.1f / 1023.0f;  
    float leitura = tensao * 100.0f;              

    Temperatura t;
    t.celsius = peso * leitura + intercept;
    t.fahrenheit = t.celsius * 9.0f / 5.0f + 32.0f;
    return t;
}
