#include "interface/LCD.h"
#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void LCD::iniciar() {
    lcd.init();
    lcd.backlight();
    lcd.clear();
}

// Tela de apresentação: mostra os integrantes do grupo uma vez só, no início.
void LCD::mostrarIntegrantes() {
    lcd.clear();
    lcd.setCursor(0, 0);          // coluna 0, linha 0 (linha de cima)
    lcd.print("Audrei Guilherme"); // 16 caracteres, cabe certinho na linha
    lcd.setCursor(0, 1);          // coluna 0, linha 1 (linha de baixo)
    lcd.print("Gabriel");
    delay(3000);                  // deixa os nomes na tela por 3 segundos
}

void LCD::mostrarTela1(const Dados& dados, bool segunda_unidade) {

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Temp: ");
    if (segunda_unidade) {
        lcd.print(dados.temperatura.fahrenheit);
        lcd.print(" F");
    } else {
        lcd.print(dados.temperatura.celsius);
        lcd.print(" C");
    }

    lcd.setCursor(0, 1);
    lcd.print("Pres: ");
    if (segunda_unidade) {
        lcd.print(dados.pressao.bar);
        lcd.print(" bar");
    } else {
        lcd.print(dados.pressao.atm);
        lcd.print(" atm");
    }
}

void LCD::mostrarTela2(const Dados& dados, bool segunda_unidade) {
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Alt: ");
    if (segunda_unidade) {
        lcd.print(dados.altitude.pes);
        lcd.print(" ft");
    } else {
        lcd.print(dados.altitude.metros);
        lcd.print(" m");
    }

    lcd.setCursor(0, 1);
    lcd.print("Lum: ");
    if (segunda_unidade) {
        lcd.print(dados.luminosidade.candle);
        lcd.print(" fc");
    } else {
        lcd.print(dados.luminosidade.lux);
        lcd.print(" lux");
    }
}

void LCD::mostrarTela3(const Dados& dados) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Umid: ");
    lcd.print(dados.umidade);
    lcd.print(" %");
}
