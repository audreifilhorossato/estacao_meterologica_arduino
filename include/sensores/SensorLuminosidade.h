#pragma once

#include <Arduino.h>
#include "sensores/SensorI.h"

class SensorLuminosidade : public ISensor {
private:
    int pino;
    bool funcionando;

public:
    explicit SensorLuminosidade(int pino);

    void iniciar() override;
    float ler() override;
    bool estaFuncionando() override;
};