#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "HW2.h"

#define PWMPin 16
#define FREQUENCY 50

int wrap; // intialize global variable wrap
int angle;

int main()
{
    stdio_init_all();
    init_PWM();
    sleep_ms(2000);
    while (true) {

        // printf("Input an angle: ");
        // scanf("%d", &angle);

        for (int i = 0; i <181; i++){
            set_servo(i);
            sleep_ms(10);
        }
        for (int i = 180; i >= 0; i--){
            set_servo(i);
            sleep_ms(10);
        }
        
    }
}

void init_PWM(){
    // initialize global variables
    wrap = 25000;

    gpio_set_function(PWMPin, GPIO_FUNC_PWM); // Set the LED Pin to be PWM
    uint slice_num = pwm_gpio_to_slice_num(PWMPin); // Get PWM slice number

    // the clock frequency is 150MHz divided by a float from 1 to 255
    float div = 150000000/(FREQUENCY*wrap); // must be between 1-255, make PWM slower

    pwm_set_clkdiv(slice_num, div); // sets the clock speed

    // set the PWM frequency and resolution
    // this sets the PWM frequency to 150MHz / div / wrap
    pwm_set_wrap(slice_num, wrap);
    pwm_set_enabled(slice_num, true); // turn on the PWM
}

void set_servo(int angle){ //Set the PWM to the desired duty cycle in %  
    pwm_set_gpio_level(PWMPin, (int)((0.038 + (angle/180.0) * 0.09) * wrap)); 
}
