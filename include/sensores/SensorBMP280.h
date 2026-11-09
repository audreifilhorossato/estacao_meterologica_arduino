#pragma once
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include "modelos/dados.h"


class SensorBMP280 {
    public:
        SensorBMP280(
            uint8_t endereco_i2c,
            float peso,
            float intercept, 
            uint16_t quantidade_amostras = 20
        );

        bool iniciar();
        Pressao ler_pressao();
        Altitude ler_altitude();
        float ler_media_pressao();
        float ler_media_altitude();
    private:
        Adafruit_BMP280 bmp;

        uint8_t endereco_i2c;
        uint16_t quantidade_amostras;

        float peso;
        float intercept;

};
