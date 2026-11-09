#pragma once
#include <Arduino.h>
#include <DHT.h> 

class SensorDHT22 {
    public:
        SensorDHT22(
            uint8_t pino,
            float peso,
            float intercept, 
        );

        void iniciar();
        float ler_umidade();

    private:
        DHT dht;

        uint8_t pino;

        float peso;
        float intercept;

};
