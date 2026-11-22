/* Minimal blocking TWI0 master (ATtiny 1-series), default pins PB0=SCL PB1=SDA. */
#pragma once
#include <stdint.h>
#include <stdbool.h>

void twi_init(uint32_t hz);
bool twi_write(uint8_t addr, uint8_t reg, const uint8_t *buf, uint8_t n);
bool twi_read(uint8_t addr, uint8_t reg, uint8_t *buf, uint8_t n);
