#include <CyberLib.h>

uint16_t N = 0;
#define C (1024)
uint8_t values[C];

// buffer for adcsra
uint8_t adcsra = B11000010; 

void setup()
{
  UART_Init(256000);
  pinMode(7, OUTPUT);
  pinMode(9, OUTPUT);
  tone(7, 440);
  
  ADMUX=B01100000;   
  delay_us(10);    
}

void loop() {
  unsigned long start = micros();
  for (N = 0; N != C; ++N) {
    ADCSRA = adcsra;
    while (ADCSRA & (1 << ADSC));
    values[N] = ADCH;
  }
  unsigned long fin = micros() - start;

  UART_SendByte(15); UART_SendByte(0); UART_SendByte(15);
  UART_SendArray(values, C);
  UART_SendArray((uint8_t *) &fin, sizeof(long)); // Время
  UART_SendByte(1); UART_SendByte(15); UART_SendByte(1);

  uint8_t data = 0;
#define cmd (data)
  if (UART_ReadByte(cmd)) {
    switch (cmd) {
      case 1: {
        if (UART_ReadByte(data) && (data <= 7)) {
          adcsra = (adcsra >> 3) << 3 | data;
        }
      }
    }
  }
}

