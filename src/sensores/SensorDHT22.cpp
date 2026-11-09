#include "sensores/SensorDHT22.h"

SensorDHT22::SensorDHT22(uint8_t pino, float peso, float intercept)
    : dht(pino, DHT22),
    pino(pino),
    peso(peso),
    intercept(intercept)
{}

void SensorDHT22::iniciar() {
    dht.begin();
}

float SensorDHT22::ler_umidade() {
    return (peso * dht.readHumidity() + intercept);
}
