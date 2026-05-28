#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "HW8.h"

int main()
{
    stdio_init_all();

    // SPI initialisation. This example will use SPI at 1MHz.
    spi_init(SPI_PORT, 1000*1000);
    gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
    gpio_set_function(PIN_CS_DAC, GPIO_FUNC_SIO);
    gpio_set_function(PIN_CS_RAM, GPIO_FUNC_SIO);
    gpio_set_function(PIN_SCK,  GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);
    
    // initialize DAC
    gpio_set_dir(PIN_CS_DAC, GPIO_OUT);
    gpio_put(PIN_CS_DAC, 1);

    // initialize RAM
    gpio_set_dir(PIN_CS_RAM, GPIO_OUT);
    gpio_put(PIN_CS_RAM, 1);

    spi_ram_init();
    ram_write_sine();
    
    while (true) {
        for(int i = 0; i <1024; i=i+2){
            update_dac_from_ram(i);
            sleep_ms(1);
        }
    }
}

static inline void cs_select(uint cs_pin) {
    asm volatile("nop \n nop \n nop"); // FIXME
    gpio_put(cs_pin, 0);
    asm volatile("nop \n nop \n nop"); // FIXME
}

static inline void cs_deselect(uint cs_pin) {
    asm volatile("nop \n nop \n nop"); // FIXME
    gpio_put(cs_pin, 1);
    asm volatile("nop \n nop \n nop"); // FIXME
}

void write_data(int channel, float v) {
    uint16_t voltage = (uint16_t)(v / 3.3f * 4095);

    uint8_t data[2];
    data[0] = 0b01110000;
    data[0] |= (channel & 0x1) << 7;            // channel select in bit 15
    data[0] |= (voltage >> 8) & 0x0F;           // top 4 bits of 12-bit value
    data[1]  = voltage & 0xFF;                   // bottom 8 bits

    cs_select(PIN_CS_DAC);
    spi_write_blocking(SPI_PORT, data, 2);
    cs_deselect(PIN_CS_DAC);
}

void spi_ram_init(){ // select ram chip and write a bit to it to tell it to co into sequential mode
    uint8_t data[2];
    int len = 2;
    data[0] = 0b00000001; // tells chip that I am writing to it
    data[1] = 0b01000000; // instruction for sequential mode
    cs_select(PIN_CS_RAM);
    spi_write_blocking(SPI_PORT, data, len); // data is a uint8_t array with length len
    cs_deselect(PIN_CS_RAM);
}

void ram_write_sine(){
    int i = 0;
    uint8_t data[2];
    uint16_t data_short = 0;
    uint8_t channel = 0b0;
    float voltage = 0;
    uint16_t addr = 0;

    for(i = 0; i < 1024; i++){

        data_short = (channel&0b1)<<15; // extract value
        data_short = data_short | (0b111<<12); // shift data

        uint16_t v = (uint16_t)((sin(2*3.14159*2*i/1024.0) + 1) * 4095.0/2.0);

        data_short = data_short | (0b111111111111 & v); // shift

        // turn 16 bit number into 8 bit
        data[0] = data_short >> 8;
        data[1] = data_short & 0xFF;;

        spi_ram_write(addr, data, 2); // write the two bits into the ram
        addr = addr + 2; // increment address
    }
}

void spi_ram_write(uint16_t addr, uint8_t * data, int len){
    uint8_t packet[5];
    packet[0] = 0b00000010; // instruction that I am going to write
    packet[1] = addr>>8; // shift address to get first 8 bits;
    packet[2] = addr & 0xFF; // second 8 bits of address
    packet[3] = data[0]; // first 8 bits of data to send
    packet[4] = data[1]; // second 8 bits of data to send

    cs_select(PIN_CS_RAM); // select RAM pin to talk to
    spi_write_blocking(SPI_PORT, packet, 5); // send data to pin
    cs_deselect(PIN_CS_RAM); // deselect ram pin
}

void update_dac_from_ram(int i){
    uint8_t data[2];
    spi_ram_read(i, data, 2);

    cs_select(PIN_CS_DAC);
    spi_write_blocking(SPI_PORT, data, 2);
    cs_deselect(PIN_CS_DAC);
}

void spi_ram_read(uint16_t addr, uint8_t * data, int len){
    uint8_t packet[5]; // create data packet of 5 bytes
    packet[0] = 0b00000011; // instruction that I am going to red
    packet[1] = addr>>8; // shift address to get first 8 bits;
    packet[2] = addr & 0xFF; // second 8 bits of address
    packet[3] = 0; // waiting for data
    packet[4] = 0; // waiting for data

    uint8_t dst[5]; // new packet of data that I am reading
    cs_select(PIN_CS_RAM);
    spi_write_read_blocking(SPI_PORT, packet, dst, 5); // read 5 bytes of data, first 3 are garbage
    cs_deselect(PIN_CS_RAM);
    data[0] = dst[3]; // extract data
    data[1] = dst[4]; // extract second byte of data
}