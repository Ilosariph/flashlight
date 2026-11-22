#include "tmag5273.h"
#include "twi.h"

enum {
    DEVICE_CONFIG_1 = 0x00,
    DEVICE_CONFIG_2 = 0x01,
    SENSOR_CONFIG_1 = 0x02,
    SENSOR_CONFIG_2 = 0x03,
    I2C_ADDRESS = 0x0C,
    MANUFACTURER_ID_LSB = 0x0E,
    T_MSB_RESULT = 0x10,
};

static bool wr(uint8_t a, uint8_t reg, uint8_t v) { return twi_write(a, reg, &v, 1); }

bool tmag_present(uint8_t a)
{
    uint8_t id[2];
    /* manufacturer ID reads 0x5449 ("TI"), LSB first */
    return twi_read(a, MANUFACTURER_ID_LSB, id, 2) && id[0] == 0x49 && id[1] == 0x54;
}

bool tmag_set_addr(uint8_t a, uint8_t new_a)
{
    return wr(a, I2C_ADDRESS, (uint8_t)(new_a << 1) | 1); /* bit0: update enable */
}

bool tmag_init(uint8_t a)
{
    return wr(a, DEVICE_CONFIG_1, 2 << 2)         /* CONV_AVG 4x, temp-comp off */
        && wr(a, SENSOR_CONFIG_1, 7 << 4)         /* MAG_CH_EN = X,Y,Z */
        && wr(a, SENSOR_CONFIG_2, 0)              /* no angle calc, ±40 mT X/Y/Z */
        && wr(a, DEVICE_CONFIG_2, 2);             /* continuous measure */
}

bool tmag_read(uint8_t a, tmag_sample_t *s)
{
    uint8_t b[8];
    if (!twi_read(a, T_MSB_RESULT, b, 8))
        return false;
    s->t = (int16_t)(b[0] << 8 | b[1]);
    s->x = (int16_t)(b[2] << 8 | b[3]);
    s->y = (int16_t)(b[4] << 8 | b[5]);
    s->z = (int16_t)(b[6] << 8 | b[7]);
    return true;
}
