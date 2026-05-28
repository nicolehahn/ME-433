#include "HW7.h"

int main()
{
    stdio_init_all();

    // SPI initialisation. This example will use SPI at 1MHz.
    spi_init(SPI_PORT, 1000*1000);
    gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
    gpio_set_function(PIN_CS,   GPIO_FUNC_SIO);
    gpio_set_function(PIN_SCK,  GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);
    
    // Chip select is active-low, so we'll initialise it to a driven-high state
    gpio_init(PIN_CS);
    gpio_set_dir(PIN_CS, GPIO_OUT);
    gpio_put(PIN_CS, 1);
    // For more examples of SPI use see https://github.com/raspberrypi/pico-examples/tree/master/spi

    float t = 0;
    while (true) {
        t += 0.01;
        // call write_data
        float voltage_1 = (sin(2*3.14159*2*t) + 1) * 3.3 / 2;
        
        float voltage_2 = ((2/3.14159)*asin(sin(2*3.14159*t)) + 1) * 3.3 / 2;
        printf("%f\r\n", voltage_2);
        write_data(0, voltage_1);
        write_data(1, voltage_2);

        sleep_ms(10);
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

    cs_select(PIN_CS);
    spi_write_blocking(SPI_PORT, data, 2);
    cs_deselect(PIN_CS);
}

