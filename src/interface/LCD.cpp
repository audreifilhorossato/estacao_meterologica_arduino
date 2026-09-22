#include "interface/LCD.h"
#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void LCD::iniciar() {
    lcd.init();
    lcd.backlight();
}

void LCD::mostrarDados(const Dados& dados) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Temp: ");
    lcd.print(dados.temperatura);
    lcd.setCursor(0, 1);
    lcd.print("Pres: ");
    lcd.print(dados.pressao);
}

