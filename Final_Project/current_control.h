#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

// Position Control Defines
#define POT_ADC_PIN 26
#define PWM_IN1_PIN 6 
#define PWM_IN2_PIN 10  

#define INA219_ADDR 0x40
#define PWM_WRAP 6250 // 125MHz / 6250 = 20kHz PWM

#define INA219_ADDR 0x40
#define PWM_WRAP 6250 // 125MHz / 6250 = 20kHz PWM

void writeINA219(uint8_t reg, uint16_t value);
int16_t readINA219(uint8_t reg);
void init_ina219();
float read_ina219();
void set_motor_pwm(float control_signal);
bool timer_callback(struct repeating_timer *t);
void init_current_control();