#include "sensores/SensorBMP280.h"

SensorBMP280::SensorBMP280( int endereco_i2c, int quantidade_amostras)
    : endereco_i2c(endereco_i2c),
    quantidade_amostras(quantidade_amostras)
{}

bool SensorBMP280::iniciar() {
    bmp.begin(endereco_i2c);
}

float SensorBMP280::ler_media_pressao() {
    float soma = 0;

    for (int i = 0; i < quantidade_amostras; i++) {
        soma += bmp.readPressure(); 
        delay(2);
    }
 
    return soma / quantidade_amostras;
}

Pressao SensorBMP280::ler_pressao(){
    float pascal = ler_media_pressao();

    Pressao p;
    p.atm = pascal / 101325.0;
    p.bar = pascal / 100000.0;
    return p;
}

float SensorBMP280::ler_media_altitude() {
    float soma = 0;
 
    for (int i = 0; i < quantidade_amostras; i++) {
        soma += bmp.readAltitude(1013.25);
        delay(2);
    }
 
    return soma / quantidade_amostras;
}

Altitude SensorBMP280::ler_altitude(){
    float leitura = ler_media_altitude();

    Altitude a;
    a.metros = leitura;
    a.pes = a.metros * 3.28084;
    return a;
}
