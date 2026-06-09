#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "hardware/adc.h"
#include "hardware/pwm.h"
#include "hardware/timer.h"
#include "hx711.h"
#include "encoder.h"

// I2C defines
#define I2C_PORT i2c0
#define I2C_SDA 8
#define I2C_SCL 9

// Filter Defines
#define A 0.1
#define AVERAGE -391500

// Position Control Defines
#define POT_ADC_PIN 26
#define PWM_IN1_PIN 6 
#define PWM_IN2_PIN 10  

#define INA219_ADDR 0x40
#define PWM_WRAP 6250 // 125MHz / 6250 = 20kHz PWM

#define INA219_ADDR 0x40
#define PWM_WRAP 6250 // 125MHz / 6250 = 20kHz PWM

bool timer_callback(struct repeating_timer *t);
void set_motor_pwm(float control_signal);
float read_ina219();
void init_ina219();
int16_t readINA219(uint8_t reg);
void writeINA219(uint8_t reg, uint16_t value);
void init_current_control();

volatile int state = 0;
volatile int cnt = 0;
volatile float e_int = 0; 
volatile float desired_current = 300.0; 

float actual_current_arr[400];
float desired_current_arr[400];

float kp = 4.0;
float ki = 0.5;

uint slice_in1, slice_in2; 
uint chan_in1, chan_in2;

int main()
{


    stdio_init_all();
    init_hx711();
    encoder_init();
    encoder_reset_position();
    init_current_control();

    adc_init();
    adc_gpio_init(POT_ADC_PIN);

    

    float average = AVERAGE;
    absolute_time_t start_time = get_absolute_time();
    int i = 0;
    int sum = 0;
    for(int i = 0; i<500; i++)
    {
        sum = sum + hx711_read_raw();
    }
    int force_average = sum/500;


    while(true){
        int data = hx711_read_raw();
        average = A * data + (1.0 - A) * average;
        uint64_t t = absolute_time_diff_us(start_time, get_absolute_time());
        float angle = get_continuous_angle();
        int average2 = average - force_average;

        float actual_current = read_ina219();
        
        if(angle > 90){
            desired_current = -1000;
        }
        else if(angle < -90){
            desired_current = 1000;
        }
        else if(angle < 20 && angle > -20){
            if(average2 > 1500 && average2 < 5500){
                desired_current = (-120*(average2/1500.0));
            }
            else if(average2 < -1500 && average2 > -5500){
                desired_current = (-120*(average2/1500.0));
            }
            else{
                desired_current = 0;
            }
        }
        else{
            desired_current = -2*angle;
        }
        
        // PI
        float error = desired_current - actual_current;
        e_int += error;
        
        float control_signal = (kp * error) + (ki * e_int);
        
        // PWM cap so it doesnt expload
        if (control_signal > PWM_WRAP) control_signal = PWM_WRAP;
        if (control_signal < -PWM_WRAP) control_signal = -PWM_WRAP;

        if(control_signal > -30.0 && control_signal < 30.0){
            control_signal = 0;
        }
        set_motor_pwm(control_signal);

        printf("%d %llu %d %d %.2f\r\n", i+1, t, data, (int)average-force_average, angle);
    }
}

// INA219
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
 
    if (control_signal >= 0) {
        pwm_set_chan_level(slice_in1, chan_in1, PWM_WRAP); 
        pwm_set_chan_level(slice_in2, chan_in2, PWM_WRAP - (uint16_t)control_signal);
    } else {
        pwm_set_chan_level(slice_in1, chan_in1, PWM_WRAP - (uint16_t)(-control_signal));
        pwm_set_chan_level(slice_in2, chan_in2, PWM_WRAP); 
    }
}

void init_current_control(){
    gpio_set_function(PWM_IN1_PIN, GPIO_FUNC_PWM);
    gpio_set_function(PWM_IN2_PIN, GPIO_FUNC_PWM);
    
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

/*        if(average2 > 1500 && average2 < 5500){
            desired_current = (-120*(average2/1500.0));
        }
        else if(average2 < -1500 && average2 > -5500){
            desired_current = (-120*(average2/1500.0));
        }
        else{
            desired_current = 0;
        }*/