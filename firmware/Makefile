MCU    ?= attiny1616
F_CPU  ?= 10000000UL
PORT   ?= /dev/ttyUSB0
TARGET  = flashlight
BUILD   = build

SRC  = $(wildcard src/*.c)
OBJ  = $(SRC:src/%.c=$(BUILD)/%.o)

# AVR_LIBC comes from the devShell (flake.nix)
DEVLIB = $(AVR_LIBC)/lib/avrxmega3
CFLAGS  = -mmcu=$(MCU) -DF_CPU=$(F_CPU) -Os -std=gnu11 -Wall -Wextra \
          -ffunction-sections -fdata-sections -Isrc
LDFLAGS = -mmcu=$(MCU) -B $(DEVLIB) -L $(DEVLIB) -Wl,--gc-sections
LDLIBS  = -lm

all: $(BUILD)/$(TARGET).hex size

$(BUILD)/%.o: src/%.c | $(BUILD)
	avr-gcc $(CFLAGS) -c $< -o $@

$(BUILD)/$(TARGET).elf: $(OBJ)
	avr-gcc $(LDFLAGS) $^ $(LDLIBS) -o $@

$(BUILD)/$(TARGET).hex: $(BUILD)/$(TARGET).elf
	avr-objcopy -O ihex -R .eeprom $< $@

$(BUILD):
	mkdir -p $@

size: $(BUILD)/$(TARGET).elf
	avr-size $<

flash: $(BUILD)/$(TARGET).hex
	avrdude -p t1616 -c serialupdi -P $(PORT) -U flash:w:$<:i

clean:
	rm -rf $(BUILD)

.PHONY: all size flash clean
