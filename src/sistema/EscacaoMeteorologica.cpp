#include "sistema/EstacaoMeteorologica.h"

EstacaoMeteorologica::EstacaoMeteorologica(
    uint8_t pino_lm35,
    float peso_lm35,
    float intercept_lm35,
    uint8_t endereco_i2c,
    float peso_bmp280,
    float intercept_bmp280,
    uint16_t quantidade_amostras,
    unsigned long intervalo_leitura
)
    : sensor_lm35(
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
      display(),
      dados{},
      momento_ultima_leitura(0),
      intervalo_leitura(intervalo_leitura) {
}

void EstacaoMeteorologica::iniciar() {

    analogReference(INTERNAL);
    delay(100);

    sensor_lm35.iniciar();
    sensor_bmp280.iniciar();
    display.iniciar();

    atualizar_dados();
    display.mostrarDados(dados);

    momento_ultima_leitura = millis();
}

void EstacaoMeteorologica::executar() {
    unsigned long momento_atual = millis();

    if ( momento_atual - momento_ultima_leitura < intervalo_leitura) {
        return;
    }

    momento_ultima_leitura = momento_atual;

    atualizar_dados();
    display.mostrarDados(dados);
}

void EstacaoMeteorologica::atualizar_dados() {
    dados.temperatura = sensor_lm35.ler_temperatura();
    dados.pressao = sensor_bmp280.ler_pressao();
    dados.altitude = sensor_bmp280.ler_altitude();
}

const Dados& EstacaoMeteorologica::obter_dados() const {
    return dados;
}