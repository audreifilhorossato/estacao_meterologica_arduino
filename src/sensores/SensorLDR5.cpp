
#include "sensores/SensorLDR5.h"

SensorLDR5::SensorLDR5(uint8_t pino, float peso, float intercept, uint16_t quantidade_amostras)
    : pino(pino),
    quantidade_amostras(quantidade_amostras),
    peso(peso),
    intercept(intercept)
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
    float tensao = ler_media() * VREF / ADC_MAX;          
    tensao = constrain(tensao, 0.001f, VREF - 0.001f);    
    float r_ldr = RESISTOR * tensao / (VCC - tensao);     
    return pow(10, peso * log10(r_ldr) + intercept);
}
