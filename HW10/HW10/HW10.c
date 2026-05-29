#include "HW10.h"

int main()
{
    stdio_init_all();

    init_buttons();

    bool buttons [4];

    while (true) {
        
        get_button_states(buttons);
        printf("(%d, %d, %d, %d)\r\n", buttons[0], buttons[1], buttons[2], buttons[3]);
        sleep_ms(100/3); // 30Hz

    }
}

void init_buttons(){
    gpio_init(P1_UP);
    gpio_init(P2_UP);
    gpio_init(P1_DOWN);
    gpio_init(P2_DOWN);

    gpio_set_dir(P1_UP, GPIO_IN);
    gpio_set_dir(P2_UP, GPIO_IN);
    gpio_set_dir(P1_DOWN, GPIO_IN);
    gpio_set_dir(P2_DOWN, GPIO_IN);

}

void get_button_states(bool *buttons){
    buttons[0] = !gpio_get(P1_UP);
    buttons[1] = !gpio_get(P1_DOWN);
    buttons[2] = !gpio_get(P2_UP);
    buttons[3] = !gpio_get(P2_DOWN);
}
