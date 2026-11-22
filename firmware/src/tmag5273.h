/* TI TMAG5273 3D Hall sensor, I2C. Register map per datasheet SBASAE5. */
#pragma once
#include <stdint.h>
#include <stdbool.h>

#define TMAG_ADDR_A1 0x35 /* factory default of the A1 variant (Adafruit 6489) */

typedef struct {
    int16_t x, y, z; /* raw, ±40 mT range → 1 LSB = 40/32768 mT */
    int16_t t;       /* raw die temperature */
} tmag_sample_t;

bool tmag_present(uint8_t addr);
bool tmag_set_addr(uint8_t addr, uint8_t new_addr);
bool tmag_init(uint8_t addr); /* XYZT, continuous, 4x averaging, ±40 mT */
bool tmag_read(uint8_t addr, tmag_sample_t *s);
