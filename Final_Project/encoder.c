#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "encoder.h"

#define I2C_PORT i2c0
#define I2C_SDA 8
#define I2C_SCL 9

#define ADDR 0x36
#define REG_ZPOS    0x01
#define REG_MANG    0x05
#define REG_STATUS  0x0B
#define REG_RAW     0x0C
#define REG_ANGLE   0x0E

void encoder_init(void) {
    i2c_init(I2C_PORT, 400000);
    gpio_set_function(I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA);
    gpio_pull_up(I2C_SCL);
}

void write_to_chip(uint8_t reg, uint8_t data){
        uint8_t buf[2];
        buf[0] = reg;
        buf[1] = data;
        i2c_write_blocking(I2C_PORT, ADDR, buf, 2, false);
    }

uint8_t read8(uint8_t reg) {
    uint8_t val;
    i2c_write_blocking(I2C_PORT, ADDR, &reg, 1, true);
    i2c_read_blocking(I2C_PORT, ADDR, &val, 1, false);
    return val;
}

uint16_t read16(uint8_t reg) {
    uint8_t buf[2];
    i2c_write_blocking(I2C_PORT, ADDR, &reg, 1, true);
    i2c_read_blocking(I2C_PORT, ADDR, buf, 2, false);
    return ((buf[0] << 8) | buf[1]) & 0x0FFF;
}

void write16(uint8_t reg, uint16_t val) {
    uint8_t buf[3] = { reg, (val >> 8) & 0x0F, val & 0xFF };
    i2c_write_blocking(I2C_PORT, ADDR, buf, 3, false);
}

float get_angle() {
    return read16(REG_ANGLE) * (360.0f / 4096.0f);
}

void set_zero() {
    write16(REG_ZPOS, read16(REG_RAW));
}

bool as5600_magnet_ok() {
    return (read8(REG_STATUS) & (1 << 5)) != 0;
}

void set_angle(float degrees) {
    uint16_t raw = read16(REG_RAW);
    uint16_t offset = (uint16_t)(degrees * 4096.0f / 360.0f);
    write16(REG_ZPOS, (raw - offset) & 0x0FFF);
}

void set_angle_limits(float min_deg, float max_deg) {
    uint16_t raw = read16(REG_RAW);
    uint16_t min_counts = (uint16_t)(min_deg * 4096.0f / 360.0f);
    uint16_t max_counts = (uint16_t)(max_deg * 4096.0f / 360.0f);

    write16(REG_ZPOS, (raw - min_counts) & 0x0FFF);
    write16(0x03, (raw + (max_counts - min_counts)) & 0x0FFF); // MPOS
}

// Add these at the top of encoder.c
static float _accumulated = 0.0f;
static float _last_angle = -1.0f;

void encoder_reset_position(void) {
    _accumulated = 0.0f;
    _last_angle = get_raw_angle();  // seed with current
}

float get_raw_angle(void) {
    return read16(REG_ANGLE) * (360.0f / 4096.0f);
}

float get_continuous_angle(void) {
    float current = get_raw_angle();

    if (_last_angle < 0.0f) {
        // First call — initialize
        _last_angle = current;
        return _accumulated;
    }

    float delta = current - _last_angle;

    // Detect rollover: a jump larger than 180° must be a wrap
    if (delta > 180.0f)  delta -= 360.0f;  // wrapped backward (CW rollover)
    if (delta < -180.0f) delta += 360.0f;  // wrapped forward  (CCW rollover)

    _accumulated += delta;
    _last_angle = current;

    return _accumulated;
}