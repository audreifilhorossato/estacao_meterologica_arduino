#pragma once

#include <Arduino.h>

#include "modelos/Dados.h"
#include "sensores/SensorLuminosidade.h"
#include "interface/LCD.h"

class EstacaoMeteorologica {
private:
    SensorLuminosidade& sensor_luminosidade;
    LCD& display;

    Dados dados;

    unsigned long instanteUltimaLeitura;
    unsigned long intervaloLeitura;

    void atualizarSensores();
    void atualizarDisplay();

public:
    EstacaoMeteorologica(
        SensorLuminosidade& luminosidade,
        LCD& display
    );

    void iniciar();
    void executar();
};