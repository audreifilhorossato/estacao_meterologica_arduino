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
        static constexpr float RESISTOR = 10000.0f;  

        static constexpr float VREF = 1.1f;    
        static constexpr float VCC = 3.3f; 

        int pino;
        int quantidade_amostras;

        float peso;
        float intercept;

};

