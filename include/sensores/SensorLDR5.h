#pragma once
#include <Arduino.h>

class SensorLDR5 {
    public:
        SensorLDR5(
            uint8_t pino,
            float peso,
            float intercept, 
            uint16_t quantidade_amostras = 20
        );

        void iniciar();
        float ler_luminosidade() const;
        float ler_media() const;

        void definir_calibracao(
            float novo_peso,
            float novo_intercept
        );

    private:

        static constexpr float RESISTOR = 10000.0f; 
        static constexpr float ADC_MAX  = 1023.0f;  

        uint8_t pino;
        uint16_t quantidade_amostras;

        float peso;
        float intercept;

};

