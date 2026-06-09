#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "hx711.h"
#include "encoder.h"

// I2C defines
#define I2C_PORT i2c0
#define I2C_SDA 8
#define I2C_SCL 9

// Filter Defines
#define A 0.1
#define AVERAGE -396500


int main()
{
    stdio_init_all();
    init_hx711();
    encoder_init();
    encoder_reset_position();

    float average = AVERAGE;
    absolute_time_t start_time = get_absolute_time();
    int i = 0;

    while(true){
        int data = hx711_read_raw();
        average = A * data + (1.0 - A) * average;
        uint64_t t = absolute_time_diff_us(start_time, get_absolute_time());
        float angle = get_continuous_angle();

        printf("%d %llu %d %d %.2f\r\n", i+1, t, data, (int)average-AVERAGE, angle);
        i++;
    }
}