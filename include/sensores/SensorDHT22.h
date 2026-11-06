// DHT22 desativado para testes: descomente o bloco abaixo para usar o sensor novamente.
/*
#pragma once
#include <Arduino.h>
#include <DHT.h> 

class SensorDHT22 {
    public:
        SensorDHT22(
            uint8_t pino,
            float peso,
            float intercept, 
            uint16_t quantidade_amostras = 20
        );

        void iniciar();
        float ler_umidade();
        float ler_media();

    private:
        DHT dht;

        uint8_t pino;
        uint16_t quantidade_amostras;

        float peso;
        float intercept;

};
*/
