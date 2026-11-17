#include "interface/LCD.h"
#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);



void LCD::iniciar() {
    lcd.init();
    lcd.createChar(0, grau);
    lcd.createChar(1, carinha);
    lcd.createChar(2, cedilha);
    lcd.createChar(3, a_til);
    lcd.backlight();
    lcd.clear();
}

void:: LCD::mostrarCapa() {
    lcd.clear();
    lcd.setCursor(0, 0);          
    lcd.print("Instrumenta");
    lcd.write(byte(2));
    lcd.write(byte(3));
    lcd.print("o e"); 
    lcd.setCursor(0, 1);          
    lcd.print("Medi");
    lcd.write(byte(2));
    lcd.write(byte(3));
    lcd.print("o"); 
    delay(3000);

    lcd.clear();
    lcd.setCursor(0, 0);          
    lcd.print("Grupo Amarelo"); 
    lcd.setCursor(0, 1);          
    lcd.print("2026");
    delay(3000);

    lcd.clear();
    lcd.setCursor(0, 0);          
    lcd.print("Audrei, Gabriel"); 
    lcd.setCursor(0, 1);          
    lcd.print("e Guilherme ");
    lcd.write(byte(1));
}

void LCD::mostrarTela1(const Dados& dados, bool segunda_unidade) {

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Temp: ");
    if (segunda_unidade) {
        lcd.print(dados.temperatura.fahrenheit);
        lcd.write(byte(0));
        lcd.print(" F");
    } else {
        lcd.print(dados.temperatura.celsius);
        lcd.write(byte(0));
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
        lcd.print(" cd");
    } else {
        lcd.print(dados.luminosidade.lux);
        lcd.print(" lx");
    }
}

void LCD::mostrarTela3(const Dados& dados) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Umid: ");
    lcd.print(dados.umidade);
    lcd.print(" %");
}
