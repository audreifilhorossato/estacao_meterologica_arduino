#pragma once

#include <Arduino.h>
#include "modelos/dados.h"

class LCD {
    public:
        void iniciar();
        void mostrarDados(const Dados& dados);
};