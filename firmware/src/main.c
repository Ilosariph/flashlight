/*
 * Bench firmware v0: ring sensing with Adafruit 5690 (ATtiny1616) +
 * 2x Adafruit 6489 (TMAG5273 A1, both 0x35 from the factory).
 *
 * Wiring
 *   sensor 1: STEMMA QT cable as is (3V3, GND, SDA PB1, SCL PB0)
 *   sensor 2: STEMMA QT chained, but its red (VIN) wire cut and fed from PA4
 *             → stays off until sensor 1 has been moved to address 0x36
 *   serial:   PB2 (TX) → RX of the USB-serial adapter, 115200 8N1
 *             (same adapter as SerialUPDI: flash, then rewire to RX)
 *
 * Output, ~20 Hz CSV:
 *   ms,x1,y1,z1,a1,x2,y2,z2,a2
 *   x/y/z in µT, a = atan2 angle in deg of the pair set by ANGLE_PAIR
 *   (sensor flat on the spine with X along the light axis → Y/Z plane).
 */
#include <avr/io.h>
#include <avr/cpufunc.h>
#include <util/delay.h>
#include <math.h>
#include "twi.h"
#include "uart.h"
#include "tmag5273.h"

#define S1 0x36
#define S2 TMAG_ADDR_A1
#define ANGLE_PAIR_YZ 1 /* 0: X/Y, 1: Y/Z, 2: X/Z */

static void clock_10mhz(void)
{
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, CLKCTRL_PDIV_2X_gc | CLKCTRL_PEN_bm);
}

static int32_t ut(int16_t raw) { return (int32_t)raw * 40000L / 32768L; }

static int16_t angle(const tmag_sample_t *s)
{
    float a;
#if ANGLE_PAIR_YZ == 0
    a = atan2f(s->y, s->x);
#elif ANGLE_PAIR_YZ == 1
    a = atan2f(s->z, s->y);
#else
    a = atan2f(s->z, s->x);
#endif
    return (int16_t)lroundf(a * 57.29578f);
}

static void report(uint8_t addr)
{
    tmag_sample_t s;
    if (!tmag_read(addr, &s)) {
        uart_puts(",err,err,err,err");
        return;
    }
    uart_putc(',');
    uart_int(ut(s.x));
    uart_putc(',');
    uart_int(ut(s.y));
    uart_putc(',');
    uart_int(ut(s.z));
    uart_putc(',');
    uart_int(angle(&s));
}

int main(void)
{
    clock_10mhz();
    PORTA.DIRSET = PIN4_bm; /* sensor 2 power, off */
    PORTA.OUTCLR = PIN4_bm;
    uart_init(115200);
    twi_init(100000);
    _delay_ms(5);
    uart_puts("\r\n# flashlight ring bench v0\r\n");

    /* sensor 1 is alone on the bus at 0x35 → move it to 0x36 */
    if (tmag_present(S2) && tmag_set_addr(S2, S1))
        _delay_ms(1);
    uart_puts(tmag_present(S1) ? "# s1 ok\r\n" : "# s1 MISSING\r\n");

    PORTA.OUTSET = PIN4_bm; /* power sensor 2, comes up at 0x35 */
    _delay_ms(5);
    uart_puts(tmag_present(S2) ? "# s2 ok\r\n" : "# s2 MISSING\r\n");

    tmag_init(S1);
    tmag_init(S2);
    uart_puts("ms,x1,y1,z1,a1,x2,y2,z2,a2\r\n");

    uint32_t ms = 0;
    for (;;) {
        uart_int(ms);
        report(S1);
        report(S2);
        uart_puts("\r\n");
        _delay_ms(50);
        ms += 50; /* approximate, ignores print time */
    }
}
