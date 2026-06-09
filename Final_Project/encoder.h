#include <stdio.h>

void encoder_init(void);

void write_to_chip(uint8_t reg, uint8_t data);
uint8_t read8(uint8_t reg);

uint16_t read16(uint8_t reg);
void write16(uint8_t reg, uint16_t val);

float get_angle();
void set_zero();
void set_angle(float degrees);

bool as5600_magnet_ok();
void set_angle_limits(float min_deg, float max_deg);

void encoder_reset_position(void);
float get_raw_angle(void);
float get_continuous_angle(void);