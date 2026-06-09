#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "current_control.h"
#include "hardware/adc.h"
#include "hardware/pwm.h"
#include "hardware/timer.h"



void writeINA219(uint8_t reg, uint16_t value) {
    uint8_t buf[3];
    buf[0] = reg;
    buf[1] = (value >> 8) & 0xFF;
    buf[2] = value & 0xFF;
    i2c_write_blocking(i2c0, INA219_ADDR, buf, 3, false);
}

int16_t readINA219(uint8_t reg) {
    uint8_t buf[2];
    i2c_write_blocking(i2c0, INA219_ADDR, &reg, 1, true); 
    i2c_read_blocking(i2c0, INA219_ADDR, buf, 2, false);
    return (int16_t)((buf[0] << 8) | buf[1]);
}

void init_ina219() {
    uint16_t ina219_calValue = 1024;
    uint16_t ina219_config = 0b0011000010001111;
    writeINA219(0x05, ina219_calValue); 
    writeINA219(0x00, ina219_config);   
}

float read_ina219() {
    int16_t value = readINA219(0x04); 
    return (float)value / 3.0f; 
}

void set_motor_pwm(float control_signal) {
    uint slice_in1, slice_in2; 
    uint chan_in1, chan_in2;
    slice_in1 = pwm_gpio_to_slice_num(PWM_IN1_PIN);
    slice_in2 = pwm_gpio_to_slice_num(PWM_IN2_PIN);
    chan_in1 = pwm_gpio_to_channel(PWM_IN1_PIN);
    chan_in2 = pwm_gpio_to_channel(PWM_IN2_PIN);
    if (control_signal >= 0) {
        pwm_set_chan_level(slice_in1, chan_in1, PWM_WRAP); 
        pwm_set_chan_level(slice_in2, chan_in2, PWM_WRAP - (uint16_t)control_signal);
    } else {
        pwm_set_chan_level(slice_in1, chan_in1, PWM_WRAP - (uint16_t)(-control_signal));
        pwm_set_chan_level(slice_in2, chan_in2, PWM_WRAP); 
    }
}

//1 kHz interupt
bool timer_callback(struct repeating_timer *t) {
    if (state == 1) {
        adc_select_input(0);
        uint16_t pos = adc_read();
        if (pos < 250 || pos > (4095 - 250)) {
            set_motor_pwm(0); // hits wall (breaks)
            return true;
        }

        // current reader
        float actual_current = read_ina219();
        
        // PI
        float error = desired_current - actual_current;
        e_int += error;
        
        float control_signal = (kp * error) + (ki * e_int);
        
        // PWM cap so it doesnt expload
        if (control_signal > PWM_WRAP) control_signal = PWM_WRAP;
        if (control_signal < -PWM_WRAP) control_signal = -PWM_WRAP;

        set_motor_pwm(control_signal);

        //data for plotting
        actual_current_arr[cnt] = actual_current;
        desired_current_arr[cnt] = desired_current;
        cnt++;

        // flip responce at 100 cycles
        if (cnt == 100 || cnt ==200 || cnt== 300) {
            desired_current = -desired_current;
        }

        // test ends at 400 cycles
        if (cnt >= 400) {
            state = 0;
            set_motor_pwm(0); 
            cnt = 0;
            e_int = 0;
            desired_current = 200.0; 
        }
    }
    return true;
}

void init_current_control(){
    adc_init();
    adc_gpio_init(POT_ADC_PIN);

    gpio_set_function(PWM_IN1_PIN, GPIO_FUNC_PWM);
    gpio_set_function(PWM_IN2_PIN, GPIO_FUNC_PWM);
    
    uint slice_in1, slice_in2; 
    uint chan_in1, chan_in2;
    slice_in1 = pwm_gpio_to_slice_num(PWM_IN1_PIN);
    slice_in2 = pwm_gpio_to_slice_num(PWM_IN2_PIN);
    chan_in1 = pwm_gpio_to_channel(PWM_IN1_PIN);
    chan_in2 = pwm_gpio_to_channel(PWM_IN2_PIN);

    pwm_set_wrap(slice_in1, PWM_WRAP - 1);
    pwm_set_wrap(slice_in2, PWM_WRAP - 1);
    
    set_motor_pwm(0); // Start braked
    
    pwm_set_enabled(slice_in1, true);
    pwm_set_enabled(slice_in2, true);

}