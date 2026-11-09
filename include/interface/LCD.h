#pragma once

#include <Arduino.h>
#include "modelos/dados.h"

class LCD {
    public:
        void iniciar();
        void mostrarTela1(const Dados& dados, bool segunda_unidade);
        void mostrarTela2(const Dados& dados, bool segunda_unidade);
};