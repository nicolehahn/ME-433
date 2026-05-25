#include "IMU_lib.h"



// helper functions

void init_IMU(){
    // I2C Initialisation. Using it at 400Khz.
    i2c_init(I2C_PORT, 400*1000);
    
    gpio_set_function(I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL, GPIO_FUNC_I2C);

    write_to_chip(PWR_MGMT_1, 0x00); // turn on chip
    write_to_chip(ACCEL_CONFIG, 0x00); // set accelerometer sensitivity to +- 2g
    write_to_chip(GYRO_CONFIG, 0x18); // set gyro sensitvity to +- 2000 degrees
}

void write_to_chip(uint8_t reg, uint8_t data){
    uint8_t buf[2];
    buf[0] = reg;
    buf[1] = data;
    i2c_write_blocking(I2C_PORT, ADDR, buf, 2, false);
}

uint8_t read_chip(uint8_t reg){
    uint8_t buf;

    i2c_write_blocking(I2C_PORT, ADDR, &reg, 1, true);  // true to keep host control of bus
    i2c_read_blocking(I2C_PORT, ADDR, &buf, 1, false);  // false - finished with bus

    return buf;
}

int16_t combine(uint8_t high, uint8_t low){
    int16_t val = (int16_t)((high << 8) | low);
    return val;
}

IMU_Data read_IMU(){
    // read all 14 output registers
    uint8_t data[14];

    i2c_write_blocking(I2C_PORT, ADDR, (uint8_t[]){ACCEL_XOUT_H}, 1, true);
    i2c_read_blocking(I2C_PORT, ADDR, data, 14, false);

    // combine data
    int16_t a_xout = combine(data[0], data[1]);
    int16_t a_yout = combine(data[2], data[3]);
    int16_t a_zout = combine(data[4], data[5]);

    int16_t t_out  = combine(data[6], data[7]);

    int16_t g_xout = combine(data[8], data[9]);
    int16_t g_yout = combine(data[10], data[11]);
    int16_t g_zout = combine(data[12], data[13]);

    // turn into readable numbers
    float a_x = a_xout*0.000061;
    float a_y = a_yout*0.000061;
    float a_z = a_zout*0.000061;

    float g_x = g_xout*0.007630;
    float g_y = g_yout*0.007630;
    float g_z = g_zout*0.007630;

    float t = (t_out/340.0) + 36.53;

    // store data
    IMU_Data d;
    d.ax = a_x;
    d.ay = a_y;
    d.az = a_z;
    d.gx = g_x;
    d.gy = g_y;
    d.gz = g_z;
    d.temp = t;

    return d;
}

bool button_event() { // edge detection
    static bool last = false;
    static uint32_t last_time = 0;

    bool cur = (gpio_get(BUTTON_PIN) == 0);
    uint32_t now = to_us_since_boot(get_absolute_time());

    bool event = (cur && !last && (now - last_time > 20000));

    if (event) last_time = now;
    last = cur;

    return event;
}