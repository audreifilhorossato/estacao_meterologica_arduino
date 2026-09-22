
#include "sensores/SensorLM35.h"

SensorLM35::SensorLM35(uint8_t pino, float peso, float intercept, uint16_t quantidade_amostras)
    : pino(pino),
    peso(peso),
    intercept(intercept),
    quantidade_amostras(quantidade_amostras)
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

float SensorLM35::ler_temperatura() const {
    float leitura = ler_media();
    return peso * leitura + intercept;
}

void SensorLM35::definir_calibracao(float novo_peso,float novo_intercept){
    peso = novo_peso;
    intercept = novo_intercept;
}