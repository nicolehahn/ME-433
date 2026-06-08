#include "hx711.h"

#define PIN_SCK 16
#define PIN_DT 17
#define clock_time_us 50

void init_hx711(){
    gpio_init(PIN_DT);
    gpio_set_dir(PIN_DT, GPIO_IN);

    gpio_init(PIN_SCK);
    gpio_set_dir(PIN_SCK, GPIO_OUT);
    gpio_put(PIN_SCK, 0);
}

int hx711_read_raw(){
    while(gpio_get(PIN_DT)){
        tight_loop_contents();
    }

    unsigned int raw = 0;
    for(int i=0; i <24; i++){
        gpio_put(PIN_SCK, 1); // pulse clock pin high
        sleep_us(clock_time_us); // wait a little bit
        raw = (raw << 1) | gpio_get(PIN_DT); // shift data and read new bit
        gpio_put(PIN_SCK, 0); // set clock pin low
        sleep_us(clock_time_us); // wait a bit
    }

    // one more pulse to set gain to 128
    gpio_put(PIN_SCK, 1); 
    sleep_us(clock_time_us);
    gpio_put(PIN_SCK, 0);
    sleep_us(clock_time_us);

    // turn 24-bit into 32-bit signed
    if(raw & 0x800000){
        raw |= 0xFF000000;
    }

    return (int)raw;
}