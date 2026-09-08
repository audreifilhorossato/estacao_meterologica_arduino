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
    lcd.print("Pressao: ");
    lcd.print(dados.pressao);
    delay(500);
    lcd.print("Umidade: ");
    lcd.print(dados.umidade);
    lcd.setCursor(0, 1);
    lcd.print("Luz: ");
    lcd.print(dados.luminosidade);
    delay(500);
}

void LCD::mostrarErro(const char* mensagem) {
    // Exibir a mensagem de erro no LCD.
}