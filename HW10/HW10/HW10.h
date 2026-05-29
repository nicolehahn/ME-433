#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"

#define P1_UP 14
#define P1_DOWN 15
#define P2_UP 21
#define P2_DOWN 16

void init_buttons();

void get_button_states();