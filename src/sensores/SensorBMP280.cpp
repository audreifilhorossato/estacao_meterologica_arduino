#include "sensores/SensorBMP280.h"

SensorBMP280::SensorBMP280( uint8_t endereco_i2c, float peso, float intercept, uint16_t quantidade_amostras)
    : endereco_i2c(endereco_i2c),
    peso(peso),
    intercept(intercept),
    quantidade_amostras(quantidade_amostras)
{}

bool SensorBMP280::iniciar() {
    if (!bmp.begin(endereco_i2c)) {
        return false; // sensor não respondeu no endereço I2C informado
    }
 
    return true;
}

float SensorBMP280::ler_media_pressao() {
    double soma = 0;
 
    for (uint16_t i = 0; i < quantidade_amostras; i++) {
        soma += bmp.readPressure(); // leitura em Pa
        delay(2);
    }
 
    return static_cast<float>(soma / quantidade_amostras);
}

float SensorBMP280::ler_pressao(){
    float leitura = ler_media_pressao();
    return (peso * leitura + intercept) /101325; 
}

float SensorBMP280::ler_media_altitude() {
    double soma = 0;
 
    for (uint16_t i = 0; i < quantidade_amostras; i++) {
        soma += bmp.readAltitude(1013.25); // leitura em AL
        delay(2);
    }
 
    return static_cast<float>(soma / quantidade_amostras);
}

float SensorBMP280::ler_altitude(){
    float leitura = ler_media_altitude();
    return (peso * leitura + intercept); 
}

void SensorBMP280::definir_calibracao(float novo_peso,float novo_intercept){
    peso = novo_peso;
    intercept = novo_intercept;
}