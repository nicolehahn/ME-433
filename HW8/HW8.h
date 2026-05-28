#include <stdio.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/adc.h"

// SPI Defines
// We are going to use SPI 0, and allocate it to the following GPIO pins
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define SPI_PORT spi0
#define PIN_MISO 16
#define PIN_CS_DAC 17
#define PIN_CS_RAM 20
#define PIN_SCK  18
#define PIN_MOSI 19

static inline void cs_select(uint cs_pin);

static inline void cs_deselect(uint cs_pin);

void write_data(int channel, float v); // aka update dac

void update_dac_from_ram(int);

void spi_ram_init(); // tell chip to go into sequential mode

void spi_ram_write(uint16_t, uint8_t *, int);

void spi_ram_read(uint16_t, uint8_t *, int);

void ram_write_sine();



//union FloatInt {
//    float f;
//    uint32_t i;
//}