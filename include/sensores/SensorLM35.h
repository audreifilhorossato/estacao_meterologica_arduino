#pragma once
#include <Arduino.h>
#include "modelos/dados.h"

class SensorLM35 {
    public:
        SensorLM35(
            int pino,
            float peso,
            float intercept, 
            int quantidade_amostras = 20
        );

        void iniciar();
        Temperatura ler_temperatura() const;
        float ler_media() const;
    private:
        int pino;
        int quantidade_amostras;

        float peso;
        float intercept;

};

