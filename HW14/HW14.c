#include <stdio.h>
#include "pico/stdlib.h"
#include "hx711.h"

// filter inputs
#define A 0.1
#define AVERAGE -396500

int main()
{
    stdio_init_all();
    init_hx711();

    int samples;
    int raw[1000];
    int IIR[1000];
    uint64_t current_time[1000];

    while (true) {
        scanf("%d", &samples);
        float average = AVERAGE;

        absolute_time_t start_time = get_absolute_time();

        for(int i=0; i<samples; i++){ // read data and filter it
            int data = hx711_read_raw();
            raw[i] = data;
            average = A*data+ (1.0 - A)*average;
            IIR[i] = (int)average;
            current_time[i]  = absolute_time_diff_us(start_time, get_absolute_time());
        }

        for(int i = 0; i<samples; i++){ // print data
            printf("%d %llu %d %d\r\n", i+1, current_time[i], raw[i], IIR[i]);
        } 


    }
}
