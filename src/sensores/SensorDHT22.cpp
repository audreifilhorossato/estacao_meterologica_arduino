#include "sensores/SensorDHT22.h"

SensorDHT22::SensorDHT22(uint8_t pino, float peso, float intercept, uint16_t quantidade_amostras)
    : pino(pino),
    peso(peso),
    intercept(intercept),
    dht(pino, DHT22)
    quantidade_amostras(quantidade_amostras)
{}

void SensorDHT22::iniciar() {

    pinMode(pino, INPUT);
    analogRead(pino); //só para eliminar a primeira leitura não confiavel
}


float SensorDHT22::ler_umidade() const {
    return (peso*DHT.readHumidity() + intercept);
}