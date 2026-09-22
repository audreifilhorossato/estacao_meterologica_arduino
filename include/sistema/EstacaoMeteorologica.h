#pragma once

#include <Arduino.h>

#include "sensores/SensorLM35.h"
#include "sensores/SensorBMP280.h"
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

            uint16_t quantidade_amostras = 20,
            unsigned long intervalo_leitura = 1000
        );

        void iniciar();
        void executar();
        const Dados& obter_dados() const;

    private:

        SensorLM35 sensor_lm35;
        SensorBMP280 sensor_bmp280;
        LCD display;
        Dados dados;

        unsigned long momento_ultima_leitura;
        unsigned long intervalo_leitura;

        void atualizar_dados();
};