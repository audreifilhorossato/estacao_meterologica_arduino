#pragma once

#include <Arduino.h>
#include "modelos/dados.h"

class LCD {
    public:
        void iniciar();
        void mostrarCapa();
        void mostrarTela1(const Dados& dados, bool segunda_unidade);
        void mostrarTela2(const Dados& dados, bool segunda_unidade);
        void mostrarTela3(const Dados& dados);

    private:
        byte grau[8] = {
            0b00110,
            0b01001,
            0b01001,
            0b00110,
            0b00000,
            0b00000,
            0b00000,
            0b00000
        };

        byte carinha[8] = {
            0b00000,
            0b01010,
            0b01010,
            0b00000,
            0b10001,
            0b01110,
            0b00000,
            0b00000
        };

        byte cedilha[8] = {
            0b01110,
            0b10001,
            0b10000,
            0b10000,
            0b10001,
            0b01110,
            0b00100,
            0b01100
        };

        byte a_til[8] = {
            0b01101,
            0b10010,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111,
            0b00000
        };
};