#include "sistema/EstacaoMeteorologica.h"

// LED de aviso de pouca luz
constexpr uint8_t PINO_LED = 2;                   // pino digital 2
constexpr float LIMIAR_LUMINOSIDADE = 100.0f;     // em lux: abaixo desse valor o LED acende (ajuste aqui)

// Botão que troca as unidades (ligado entre o D1 e o GND)
constexpr uint8_t PINO_BOTAO = 1;

// false = primeira unidade (°C, atm, m, lux) | true = segunda unidade (°F, bar, pés, fc)
volatile bool segunda_unidade = false;

// Troca a unidade quando o botão é apertado.
void ao_apertar_botao() {
    static unsigned long ultimo_aperto = 0;
    unsigned long agora = millis();

    if (agora - ultimo_aperto > 250) {   // ignora o "tremido" do botão (debounce)
        segunda_unidade = !segunda_unidade;
        ultimo_aperto = agora;
    }
}

// Interrupção do D1 (no Uno o D1 fica no grupo PCINT2, pinos D0 a D7).
// Ela é chamada sozinha quando o pino muda, assim o aperto não se perde
// mesmo durante os delays do display.
ISR(PCINT2_vect) {
    if (digitalRead(PINO_BOTAO) == LOW) {   // LOW = botão apertado
        ao_apertar_botao();
    }
}

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

    // uint8_t pino_dht22,      // DHT22 desativado
    // float peso_dht22,        // DHT22 desativado
    // float intercept_dht22,   // DHT22 desativado

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

      // sensor_dht22(            // DHT22 desativado
      //   pino_dht22,
      //   peso_dht22,
      //   intercept_dht22,
      //   quantidade_amostras
      // ),

      display(),
      dados{} {
}

void EstacaoMeteorologica::iniciar() {

    analogReference(INTERNAL);
    delay(100);

    sensor_lm35.iniciar();
    sensor_bmp280.iniciar();
    sensor_ldr5.iniciar();
    // sensor_dht22.iniciar();  // DHT22 desativado
    display.iniciar();

    pinMode(PINO_LED, OUTPUT);
    digitalWrite(PINO_LED, LOW);

    pinMode(PINO_BOTAO, INPUT_PULLUP);
    PCICR  |= (1 << PCIE2);     // liga as interrupções do grupo D0 a D7
    PCMSK2 |= (1 << PCINT17);   // só do pino D1

    atualizar_dados();
    display.mostrarDados(dados, segunda_unidade);
}

void EstacaoMeteorologica::executar() {
    atualizar_dados();

    // acende o LED quando a luminosidade ficar abaixo do limiar
    if (dados.luminosidade.lux < LIMIAR_LUMINOSIDADE) {
        digitalWrite(PINO_LED, HIGH);
    } else {
        digitalWrite(PINO_LED, LOW);
    }

    display.mostrarDados(dados, segunda_unidade);
}

void EstacaoMeteorologica::atualizar_dados() {
    dados.temperatura = sensor_lm35.ler_temperatura();
    dados.pressao = sensor_bmp280.ler_pressao();
    dados.altitude = sensor_bmp280.ler_altitude();
    dados.luminosidade = sensor_ldr5.ler_luminosidade();
    // dados.umidade = sensor_dht22.ler_umidade();  // DHT22 desativado
}

const Dados& EstacaoMeteorologica::obter_dados() const {
    return dados;
}