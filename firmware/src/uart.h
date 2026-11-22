/* USART0 TX only, default pin PB2, 8N1. */
#pragma once
#include <stdint.h>

void uart_init(uint32_t baud);
void uart_putc(char c);
void uart_puts(const char *s);
void uart_int(int32_t v);
