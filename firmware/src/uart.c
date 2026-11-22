#include <avr/io.h>
#include <stdlib.h>
#include "uart.h"

void uart_init(uint32_t baud)
{
    PORTB.DIRSET = PIN2_bm;
    USART0.BAUD = (uint16_t)((4UL * F_CPU + baud / 2) / baud);
    USART0.CTRLB = USART_TXEN_bm;
}

void uart_putc(char c)
{
    while (!(USART0.STATUS & USART_DREIF_bm)) {
    }
    USART0.TXDATAL = c;
}

void uart_puts(const char *s)
{
    while (*s)
        uart_putc(*s++);
}

void uart_int(int32_t v)
{
    char b[12];
    uart_puts(ltoa(v, b, 10));
}
