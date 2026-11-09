#include "interface/LCD.h"
#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void LCD::iniciar() {
    lcd.init();
    lcd.backlight();
    lcd.clear();
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
        lcd.print(dados.luminosidade.footcandle);
        lcd.print(" fc");
    } else {
        lcd.print(dados.luminosidade.lux);
        lcd.print(" lux");
    }
}

