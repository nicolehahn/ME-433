#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "HW5.h"

// I2C defines
// This example will use I2C0 on GPIO8 (SDA) and GPIO9 (SCL) running at 400KHz.
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments




int main()
{
    stdio_init_all();

    // I2C Initialisation. Using it at 400Khz.
    i2c_init(I2C_PORT, 400*1000);
    
    gpio_set_function(I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL, GPIO_FUNC_I2C);

    write_to_chip(PWR_MGMT_1, 0x00); // turn on chip
    write_to_chip(ACCEL_CONFIG, 0x00); // set accelerometer sensitivity to +- 2g
    write_to_chip(GYRO_CONFIG, 0x18); // set gyro sensitvity to +- 2000 degrees

    while (true) {
        sleep_ms(1000);

        // read all 14 output registers
        uint8_t data[14];

        i2c_write_blocking(i2c_default, ADDR, (uint8_t[]){ACCEL_XOUT_H}, 1, true);
        i2c_read_blocking(i2c_default, ADDR, data, 14, false);

        // combine data
        int16_t a_xout = combine(data[0], data[1]);
        int16_t a_yout = combine(data[2], data[3]);
        int16_t a_zout = combine(data[4], data[5]);

        int16_t t_out  = combine(data[6], data[7]);

        int16_t g_xout = combine(data[8], data[9]);
        int16_t g_yout = combine(data[10], data[11]);
        int16_t g_zout = combine(data[12], data[13]);

        /* accelerometer
        uint8_t a_xout_h = read_chip(ACCEL_XOUT_H);
        uint8_t a_xout_l = read_chip(ACCEL_XOUT_L);
        uint8_t a_yout_h = read_chip(ACCEL_YOUT_H);
        uint8_t a_yout_l = read_chip(ACCEL_YOUT_L);
        uint8_t a_zout_h = read_chip(ACCEL_ZOUT_H);
        uint8_t a_zout_l = read_chip(ACCEL_ZOUT_L);

        // gyroscope
        uint8_t g_xout_h = read_chip(GYRO_XOUT_H);
        uint8_t g_xout_l = read_chip(GYRO_XOUT_L);
        uint8_t g_yout_h = read_chip(GYRO_YOUT_H);
        uint8_t g_yout_l = read_chip(GYRO_YOUT_L);
        uint8_t g_zout_h = read_chip(GYRO_ZOUT_H);
        uint8_t g_zout_l = read_chip(GYRO_ZOUT_L);

        // thermometer
        uint8_t t_out_h = read_chip(TEMP_OUT_H);
        uint8_t t_out_l = read_chip(TEMP_OUT_L);

        // combine into 16 bit signed ints
        int16_t a_xout = combine(a_xout_h, a_xout_l);
        int16_t a_yout = combine(a_yout_h, a_yout_l);
        int16_t a_zout = combine(a_zout_h, a_zout_l);

        int16_t g_xout = combine(g_xout_h, g_xout_l);
        int16_t g_yout = combine(g_yout_h, g_yout_l);
        int16_t g_zout = combine(g_zout_h, g_zout_l);

        int16_t t_out = combine(t_out_h, t_out_l);

        */

        // turn outputs into readable values;

        float a_x = a_xout*0.000061;
        float a_y = a_yout*0.000061;
        float a_z = a_zout*0.000061;

        float g_x = g_xout*0.007630;
        float g_y = g_yout*0.007630;
        float g_z = g_zout*0.007630;

        float t = (t_out/340.0) + 36.53;

        // print outputs
        printf("x accel: %f\r\n", a_x);
        printf("y accel: %f\r\n", a_y);
        printf("z accel: %f\r\n", a_z);

        printf("x gyro: %f\r\n", g_x);
        printf("y gyro: %f\r\n", g_y);
        printf("z gyro: %f\r\n", g_z);

        printf("temp: %f\r\n", t);


    }


}


void write_to_chip(uint8_t reg, uint8_t data){
    uint8_t buf[2];
    buf[0] = reg;
    buf[1] = data;
    i2c_write_blocking(i2c_default, ADDR, buf, 2, false);
}

uint8_t read_chip(uint8_t reg){
    uint8_t buf;

    i2c_write_blocking(i2c_default, ADDR, &reg, 1, true);  // true to keep host control of bus
    i2c_read_blocking(i2c_default, ADDR, &buf, 1, false);  // false - finished with bus

    return buf;
}

int16_t combine(uint8_t high, uint8_t low){
    int16_t val = (int16_t)((high << 8) | low);
    return val;
}

