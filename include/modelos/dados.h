#pragma once

struct Temperatura {
    float celsius = 0.0;
    float fahrenheit = 0.0;
};

struct Pressao {
    float atm = 0.0;
    float bar = 0.0;
};

struct Altitude {
    float metros = 0.0;
    float pes = 0.0;
};

struct Luminosidade {
    float lux = 0.0;
    float footcandle = 0.0;
};

struct Dados {
    Temperatura temperatura;
    Pressao pressao;
    Altitude altitude;
    Luminosidade luminosidade;
    float umidade = 0.0;
};