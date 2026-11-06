// DHT22 desativado para testes: descomente o bloco abaixo para usar o sensor novamente.
/*
#include "sensores/SensorDHT22.h"

SensorDHT22::SensorDHT22(uint8_t pino, float peso, float intercept, uint16_t quantidade_amostras)
    : dht(pino, DHT22),
    pino(pino),
    quantidade_amostras(quantidade_amostras),
    peso(peso),
    intercept(intercept)
{}

void SensorDHT22::iniciar() {
    dht.begin();
}

float SensorDHT22::ler_media() {
    // o DHT22 só atualiza a leitura a cada ~2 s, então não adianta tirar várias amostras seguidas
    return dht.readHumidity();
}

float SensorDHT22::ler_umidade() {
    return (peso * ler_media() + intercept);
}
*/
