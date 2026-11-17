
#include "sensores/SensorLDR5.h"

SensorLDR5::SensorLDR5(int pino, float peso, float intercept, int quantidade_amostras)
    : pino(pino),
    quantidade_amostras(quantidade_amostras),
    peso(peso),
    intercept(intercept)
{}

void SensorLDR5::iniciar() {

    pinMode(pino, INPUT);
    analogRead(pino); 
}

float SensorLDR5::ler_media() const {
    float soma = 0; 

    for (int i = 0; i < quantidade_amostras; i++) {
        soma += analogRead(pino);
        delay(2);
    }

    return soma / quantidade_amostras;
}

Luminosidade SensorLDR5::ler_luminosidade() const {
    float tensao = ler_media() * 1.1 / 1024.0;     
    float r_ldr = RESISTOR * tensao / (3.3 - tensao);     

    Luminosidade l;
    l.lux = pow(10, peso * log10(r_ldr) + intercept);
    l.candle = l.lux / 10.764;
    return l;
}
