
#include "sensores/SensorLM35.h"

SensorLM35::SensorLM35(int pino, float peso, float intercept, int quantidade_amostras)
    : pino(pino),
    quantidade_amostras(quantidade_amostras),
    peso(peso),
    intercept(intercept)
{}

void SensorLM35::iniciar() {

    pinMode(pino, INPUT);
    analogRead(pino);
}

float SensorLM35::ler_media() const {
    float soma = 0; 

    for (int i = 0; i < quantidade_amostras; i++) {
        soma += analogRead(pino);
        delay(2);
    }

    return soma / quantidade_amostras;
}

Temperatura SensorLM35::ler_temperatura() const {
    float tensao = ler_media() * 1.1 / 1024.0;  
    float leitura = tensao * 100.0;              

    Temperatura t;
    t.celsius = peso * leitura + intercept;
    t.fahrenheit = t.celsius * 9.0 / 5.0 + 32.0;
    return t;
}
