#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "ssd1306.h"
#include "font.h"
#include "hardware/gpio.h"

// I2C defines
#define I2C_PORT i2c0
#define I2C_SDA 12
#define I2C_SCL 13

#define ADDR 0x68

// config registers
#define CONFIG 0x1A
#define GYRO_CONFIG 0x1B
#define ACCEL_CONFIG 0x1C
#define PWR_MGMT_1 0x6B
#define PWR_MGMT_2 0x6C
// sensor data registers:
#define ACCEL_XOUT_H 0x3B
#define ACCEL_XOUT_L 0x3C
#define ACCEL_YOUT_H 0x3D
#define ACCEL_YOUT_L 0x3E
#define ACCEL_ZOUT_H 0x3F
#define ACCEL_ZOUT_L 0x40
#define TEMP_OUT_H   0x41
#define TEMP_OUT_L   0x42
#define GYRO_XOUT_H  0x43
#define GYRO_XOUT_L  0x44
#define GYRO_YOUT_H  0x45
#define GYRO_YOUT_L  0x46
#define GYRO_ZOUT_H  0x47
#define GYRO_ZOUT_L  0x48
#define WHO_AM_I     0x75

// display defines
#define CENTER_X 64
#define CENTER_Y 17

#define BUTTON_PIN 20

// data type definitions
typedef struct {
    float ax, ay, az;
    float gx, gy, gz;
    float temp;
} IMU_Data;

// function declarations
void init_IMU();
void write_to_chip(uint8_t reg, uint8_t data);
uint8_t read_chip(uint8_t reg);
int16_t combine(uint8_t high, uint8_t low);
bool button_event();
IMU_Data read_IMU();


