#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "ssd1306.h"
#include "font.h"
#include "hardware/adc.h"


// I2C defines
// This example will use I2C0 on GPIO8 (SDA) and GPIO9 (SCL) running at 400KHz.
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define I2C_PORT i2c0
#define I2C_SDA 8
#define I2C_SCL 9
#define ADC 26

// define functions
void drawLetter(unsigned char x, unsigned char y, unsigned char letter);
void drawMessage(unsigned char x, unsigned char y, unsigned char message[]);
void init_ADC();
float getVoltage();

uint64_t time;


int main()
{
    stdio_init_all();
    init_ADC();

    // I2C Initialisation. Using it at 400Khz.
    i2c_init(I2C_PORT, 800*1000);
    
    gpio_set_function(I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL, GPIO_FUNC_I2C);

    ssd1306_setup();

    uint64_t time = to_us_since_boot(get_absolute_time());

    while (true) {
        float voltage = getVoltage();
        char message[32];
        sprintf(message, "ADC output: %.2f", voltage);
        drawMessage(0, 0, message);
        
        uint64_t new_time = to_us_since_boot(get_absolute_time());
        uint64_t diff = new_time - time - 1000000;
        time = new_time;

        float fps = 1000000.0f / diff;

        char message2[32];
        sprintf(message2, "FPS: %.2f", fps);

        drawMessage(0, 8, message2);
        sleep_ms(1000);
        ssd1306_update();
}
}

void drawLetter(unsigned char x, unsigned char y, unsigned char letter){
    for(int i = 0; i < 5; i++){ // loop through columns
        char column = ASCII[letter - 0x20][i];
        for(int j = 0; j < 8; j++){
            bool bit = ((column >> j) & 0x1);
            ssd1306_drawPixel(x+i, y+j, bit);
        }
    }
    // ssd1306_update(); // to make letters appear individually
}

void drawMessage(unsigned char x, unsigned char y, unsigned char message[]){
    int i = 0; // charachter index
    int h = 0; // horizontal character placement
    int v = 0; // vertical character placement
    while(message[i] != 0){
        drawLetter(x+h, y+v, message[i]);

        
        // prevent word rollover
        int left = (127 - h) / 6; // see how many more characters can fit
        for(int c = 1; c <= left; c++){ // look at the next characters that will fit on the line
            if(message[i+c] == ' ' || message[i+c] == '\0'){ // if there is a space in there it's all good so continue to print
                break;
            }
            else if(c == left){ // if it reaches the end of the loop with no space that means the word won't fit
                h = 0; // reset horizontal counter
                v = v + 8; // go to next line
            }
        }
            
        i++;
        h = h + 6; // increment horizontal placement by one letter plus one space

        /* prevent letter rollover
        if(h + 6 > 127){ // check to see if next letter will run off screen
            h = 0;
            v = v + 8; // go to next row
        }
        */
    }
}

void init_ADC(){
    // turn on adc pin
    adc_init();
    adc_gpio_init(ADC); // pin 26
    adc_select_input(0); // knows that pin 26 is adc 0
}

float getVoltage(){
    uint16_t output = adc_read(); // get output value

    float voltage = output;///4095.0*3.3; // convert to volts
    return voltage;
}
