#pragma once

class ISensor {
public:
    virtual void iniciar() = 0;
    virtual float ler() = 0;
    virtual bool estaFuncionando() = 0;

    virtual ~ISensor() = default;
};