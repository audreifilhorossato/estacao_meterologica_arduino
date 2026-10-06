
#include "sensores/SensorLDR5.h"

SensorLDR5::SensorLDR5(uint8_t pino, float peso, float intercept, uint16_t quantidade_amostras)
    : pino(pino),
    peso(peso),
    intercept(intercept),
    quantidade_amostras(quantidade_amostras)
{}

void SensorLDR5::iniciar() {

    pinMode(pino, INPUT);
    analogRead(pino); //só para eliminar a primeira leitura não confiavel
}

float SensorLDR5::ler_media() const {
    unsigned long soma = 0;

    for (uint16_t i = 0; i < quantidade_amostras; i++) {
        soma += analogRead(pino);
        delay(2);
    }

    return static_cast<float>(soma) / quantidade_amostras;
}

float SensorLDR5::ler_luminosidade() const {
    float leitura = constrain(ler_media(), 1.0f, ADC_MAX - 1.0f);
    float r_ldr = RESISTOR * (ADC_MAX - leitura) / leitura;   
    return pow(10, peso * log10(r_ldr) + intercept);          
}

void SensorLDR5::definir_calibracao(float novo_peso,float novo_intercept){
    peso = novo_peso;
    intercept = novo_intercept;
}