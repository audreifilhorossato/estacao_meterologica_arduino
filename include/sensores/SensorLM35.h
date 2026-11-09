#pragma once
#include <Arduino.h>
#include "modelos/dados.h"

class SensorLM35 {
    public:
        SensorLM35(
            uint8_t pino,
            float peso,
            float intercept, 
            uint16_t quantidade_amostras = 20
        );

        void iniciar();
        Temperatura ler_temperatura() const;
        float ler_media() const;
    private:
        uint8_t pino;
        uint16_t quantidade_amostras;

        float peso;
        float intercept;

};

