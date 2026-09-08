#pragma once

#include <Arduino.h>
#include "modelos/Dados.h"

class LCD {
    public:
        void iniciar();
        void mostrarDados(const Dados& dados);
        void mostrarErro(const char* mensagem);
};