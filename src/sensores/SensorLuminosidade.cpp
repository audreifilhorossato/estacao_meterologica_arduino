#include "sensores/SensorLuminosidade.h"

SensorLuminosidade::SensorLuminosidade(int pino)
    : pino(pino), funcionando(false) {
}

void SensorLuminosidade::iniciar() {
    pinMode(pino, INPUT);
    funcionando = true;
}

float SensorLuminosidade::ler() {
    int leitura = analogRead(pino);
    
    float luminosidade = leitura * 0.1;

    return luminosidade;
}

bool SensorLuminosidade::estaFuncionando() {
    return funcionando;
}