#pragma once
#include <Arduino.h>
#include "modelos/dados.h"

class SensorLDR5 {
    public:
        SensorLDR5(
            int pino,
            float peso,
            float intercept, 
            int quantidade_amostras = 20
        );

        void iniciar();
        Luminosidade ler_luminosidade() const;
        float ler_media() const;

    private:
        const float RESISTOR = 10000.0;  

        int pino;
        int quantidade_amostras;

        float peso;
        float intercept;

};

