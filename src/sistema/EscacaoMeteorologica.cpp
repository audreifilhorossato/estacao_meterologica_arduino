#include "sistema/EstacaoMeteorologica.h"

constexpr uint8_t PINO_LED = 2;
constexpr uint8_t PINO_BOTAO = 3;
constexpr float LIMIAR_LUMINOSIDADE = 100000.0f;

EstacaoMeteorologica::EstacaoMeteorologica(
    uint8_t pino_lm35,
    float peso_lm35,
    float intercept_lm35,

    uint8_t endereco_i2c,
    float peso_bmp280,
    float intercept_bmp280,

    uint8_t pino_ldr5,
    float peso_ldr5,
    float intercept_ldr5,

    uint8_t pino_dht22,
    float peso_dht22,
    float intercept_dht22,

    uint16_t quantidade_amostras
)
    :sensor_lm35(
        pino_lm35,
        peso_lm35,
        intercept_lm35,
        quantidade_amostras
      ),

      sensor_bmp280(
        endereco_i2c,
        peso_bmp280,
        intercept_bmp280,
        quantidade_amostras
      ),

      sensor_ldr5(
        pino_ldr5,
        peso_ldr5,
        intercept_ldr5,
        quantidade_amostras
      ),

      sensor_dht22(
        pino_dht22,
        peso_dht22,
        intercept_dht22
      ),

      display(),
      dados{},
      segunda_unidade(false) {
}

void EstacaoMeteorologica::iniciar() {

    analogReference(INTERNAL);
    delay(100);

    sensor_lm35.iniciar();
    sensor_bmp280.iniciar();
    sensor_ldr5.iniciar();
    sensor_dht22.iniciar();
    display.iniciar();

    pinMode(PINO_LED, OUTPUT);
    digitalWrite(PINO_LED, LOW);

    pinMode(PINO_BOTAO, INPUT_PULLUP);

}

void EstacaoMeteorologica::executar() {

    display.mostrarTela1(dados, segunda_unidade);
    esperar(2000);

    display.mostrarTela2(dados, segunda_unidade);
    esperar(2000);

    display.mostrarTela3(dados);
    esperar(2000);
}

void EstacaoMeteorologica::esperar(unsigned long tempo) {
    
    unsigned long inicio = millis();

    while (millis() - inicio < tempo) {
        atualizar_dados();
        
        if (digitalRead(PINO_BOTAO) == LOW) {
            segunda_unidade = !segunda_unidade;
            delay(50);
        }

        if (dados.luminosidade.lux < LIMIAR_LUMINOSIDADE) {
            digitalWrite(PINO_LED, HIGH);
        } else {
            digitalWrite(PINO_LED, LOW);
        }
    }
}

void EstacaoMeteorologica::atualizar_dados() {
    dados.temperatura = sensor_lm35.ler_temperatura();
    dados.pressao = sensor_bmp280.ler_pressao();
    dados.altitude = sensor_bmp280.ler_altitude();
    dados.luminosidade = sensor_ldr5.ler_luminosidade();
    dados.umidade = sensor_dht22.ler_umidade();
}

const Dados& EstacaoMeteorologica::obter_dados() const {
    return dados;
}