#include <avr/io.h>
#include "twi.h"

#define TIMEOUT 20000u

void twi_init(uint32_t hz)
{
    TWI0.MBAUD = (uint8_t)(F_CPU / (2 * hz) - 5);
    TWI0.MCTRLA = TWI_ENABLE_bm;
    TWI0.MSTATUS = TWI_BUSSTATE_IDLE_gc;
}

static bool wait(uint8_t flag)
{
    for (uint16_t t = 0; t < TIMEOUT; t++) {
        uint8_t s = TWI0.MSTATUS;
        if (s & (TWI_ARBLOST_bm | TWI_BUSERR_bm))
            return false;
        if (s & flag)
            return !(s & TWI_RXACK_bm) || flag == TWI_RIF_bm;
    }
    return false;
}

static void stop(void) { TWI0.MCTRLB = TWI_MCMD_STOP_gc; }

static bool start(uint8_t addr, uint8_t reg)
{
    TWI0.MADDR = addr << 1;
    if (!wait(TWI_WIF_bm))
        return false;
    TWI0.MDATA = reg;
    return wait(TWI_WIF_bm);
}

bool twi_write(uint8_t addr, uint8_t reg, const uint8_t *buf, uint8_t n)
{
    bool ok = start(addr, reg);
    while (ok && n--) {
        TWI0.MDATA = *buf++;
        ok = wait(TWI_WIF_bm);
    }
    stop();
    return ok;
}

bool twi_read(uint8_t addr, uint8_t reg, uint8_t *buf, uint8_t n)
{
    bool ok = start(addr, reg);
    if (ok) {
        TWI0.MADDR = (addr << 1) | 1; /* repeated start */
        while (n--) {
            if (!(ok = wait(TWI_RIF_bm)))
                break;
            *buf++ = TWI0.MDATA;
            /* ACK + read next, or NACK + stop on the last byte */
            TWI0.MCTRLB = n ? TWI_MCMD_RECVTRANS_gc
                            : (TWI_ACKACT_bm | TWI_MCMD_STOP_gc);
        }
    }
    if (!ok)
        stop();
    return ok;
}
