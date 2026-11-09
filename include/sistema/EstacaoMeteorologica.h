#pragma once

#include <Arduino.h>

#include "sensores/SensorLM35.h"
#include "sensores/SensorBMP280.h"
#include "sensores/SensorLDR5.h"
#include "sensores/SensorDHT22.h"
#include "interface/LCD.h"
#include "modelos/dados.h"


class EstacaoMeteorologica {
    public:
        EstacaoMeteorologica(
            uint8_t pino_lm35,
            float peso_lm35,
            float intercept_lm35,

            uint8_t endereco_i2c,
            float peso_bmp280,
            float intercept_bmp280,

            uint8_t pino_ldr5,
            float peso_ldr5,
            float intercept_ldr5,

            uint8_t pino_dht22,
            float peso_dht22,
            float intercept_dht22,

            uint16_t quantidade_amostras = 20
        );

        void iniciar();
        void executar();
        const Dados& obter_dados() const;

    private:

        SensorLM35 sensor_lm35;
        SensorBMP280 sensor_bmp280;
        SensorLDR5 sensor_ldr5;
        SensorDHT22 sensor_dht22;

        LCD display;
        Dados dados;
        bool segunda_unidade;

        void atualizar_dados();
        void esperar(unsigned long tempo);
};