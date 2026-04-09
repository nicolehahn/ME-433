#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

// I2C defines
// This example will use I2C0 on GPIO8 (SDA) and GPIO9 (SCL) running at 400KHz.
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define I2C_PORT i2c0
#define I2C_SDA 8
#define I2C_SCL 9

#define ADDR 0x20 // hardware pins wired low
#define IODIR 0x00 // register to set direction
#define GPIO  0x09 // register to read input
#define OLAT  0x0A // register to write to output

// define functions
void write_to_chip(uint8_t reg, uint8_t data);
void read_chip(uint8_t reg);


int main()
{
    stdio_init_all();

    // I2C Initialisation. Using it at 400Khz.
    i2c_init(I2C_PORT, 400*1000);
    
    gpio_set_function(I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL, GPIO_FUNC_I2C);

    write_to_chip(IODIR, 0x7F); // set GP7 to output and all others to inputs

    // For more examples of I2C use see https://github.com/raspberrypi/pico-examples/tree/master/i2c

    int index = 0; // initialize index for blinking

    while (true) {
        printf("Hello, world!\n");
        sleep_ms(1000);

        // blink light
        if(index % 2 == 0){
            write_to_chip(OLAT, 0x80); // set GP7 to high
        }
        else{
            write_to_chip(OLAT, 0x00); // set GP7 to low
        }


    }

    
}

void write_to_chip(uint8_t reg, uint8_t data){
        uint8_t buf[2];
        buf[0] = reg;
        buf[1] = data;
        i2c_write_blocking(i2c_default, ADDR, buf, 2, false);
    }

void read_chip(uint8_t reg){
        uint8_t buf;

        i2c_write_blocking(i2c_default, ADDR, &reg, 1, true);  // true to keep host control of bus
        i2c_read_blocking(i2c_default, ADDR, &buf, 1, false);  // false - finished with bus
    }
