#pragma once
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include "modelos/dados.h"


class SensorBMP280 {
    public:
        SensorBMP280(
            int endereco_i2c,
            int quantidade_amostras = 20
        );

        bool iniciar();
        Pressao ler_pressao();
        Altitude ler_altitude();
        float ler_media_pressao();
        float ler_media_altitude();
        
    private:
        Adafruit_BMP280 bmp;

        int endereco_i2c;
        int quantidade_amostras;

};
