
#include "sensores/SensorLDR5.h"

SensorLDR5::SensorLDR5(int pino, float peso, float intercept, int quantidade_amostras)
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
    long soma = 0; // long: 20 leituras x 1023 quase estoura o int (máx. 32767)

    for (int i = 0; i < quantidade_amostras; i++) {
        soma += analogRead(pino);
        delay(2);
    }

    return static_cast<float>(soma) / quantidade_amostras;
}

Luminosidade SensorLDR5::ler_luminosidade() const {
    float tensao = ler_media() * VREF / 1024.0;     
    float r_ldr = RESISTOR * tensao / (VCC - tensao);     

    Luminosidade l;
    l.lux = pow(10, peso * log10(r_ldr) + intercept);
    l.candle = l.lux / 10.764f;
    return l;
}
