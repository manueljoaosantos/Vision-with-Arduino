#include <LiquidCrystal_I2C.h>   // Biblioteca para usar LCD com interface I2C

// Cria o objeto do LCD no endereço I2C 0x27, com 16 colunas e 2 linhas
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Variável para armazenar o dado recebido via Serial
char incomingData;

void setup()
{
    lcd.begin();            // Inicializa o LCD
    lcd.backlight();        // Liga a luz de fundo do LCD (importante em muitos modelos)
    Serial.begin(9600);     // Inicializa a comunicação serial com baud rate 9600

    lcd.setCursor(0, 0);    // Define o cursor na coluna 0, linha 0 (primeira posição)
    lcd.print("WAITTING"); // Mostra mensagem inicial
}

void loop()
{
    // Verifica se existe algum dado disponível para ler da porta Serial
    if (Serial.available() > 0)
    {
        incomingData = Serial.read();  // Lê um caractere enviado pelo Python

        if (incomingData == 'A')       // Se receber 'A' → boca aberta / sorriso
        {
            lcd.clear();               // Limpa o LCD antes de escrever
            lcd.setCursor(0, 0);       // Coloca o cursor no início
            lcd.print("SORRISO");      // Mostra "SORRISO"
        }
        else if (incomingData == 'B')  // Se receber 'B' → boca fechada / triste
        {
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("TRISTE");
        }
    }
}
