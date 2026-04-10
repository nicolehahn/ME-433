#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "ssd1306.h"
#include "font.h"

// I2C defines
// This example will use I2C0 on GPIO8 (SDA) and GPIO9 (SCL) running at 400KHz.
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define I2C_PORT i2c0
#define I2C_SDA 8
#define I2C_SCL 9

// define functions
void drawLetter(unsigned char x, unsigned char y, unsigned char letter);
void drawMessage(unsigned char x, unsigned char y, unsigned char message[]);

int main()
{
    stdio_init_all();

    // I2C Initialisation. Using it at 400Khz.
    i2c_init(I2C_PORT, 400*1000);
    
    gpio_set_function(I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL, GPIO_FUNC_I2C);

    ssd1306_setup();
    while (true) {
        /*
        sleep_ms(100);
        drawLetter(0, 0,'H');
        sleep_ms(100);
        drawLetter(6, 0, 'E');
        sleep_ms(100);
        drawLetter(12, 0, 'L');
        sleep_ms(100);
        drawLetter(18, 0, 'L');
        sleep_ms(100);
        drawLetter(24, 0, 'O');
        sleep_ms(100);
        ssd1306_clear();
        */
        drawMessage(0, 0, "If you are reading this it's already too late...");
        sleep_ms(1000);
        ssd1306_clear();
        drawMessage(0, 0, "This message will self destruct in 10 seconds.");
        drawMessage(0, 0, "This message will self destruct in 9 seconds.");
        drawMessage(0, 0, "This message will self destruct in 8 seconds.");
        drawMessage(0, 0, "This message will self destruct in 7 seconds.");
        drawMessage(0, 0, "This message will self destruct in 6 seconds.");
        drawMessage(0, 0, "This message will self destruct in 5 seconds.");
        drawMessage(0, 0, "This message will self destruct in 4 seconds.");
        drawMessage(0, 0, "This message will self destruct in 3 seconds.");
        drawMessage(0, 0, "This message will self destruct in 2 seconds.");
        drawMessage(0, 0, "This message will self destruct in 1 seconds.");
        drawMessage(0, 0, "This message will self destruct in 0 seconds.");
        sleep_ms(1000);

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
    ssd1306_update();
}

void drawMessage(unsigned char x, unsigned char y, unsigned char message[]){
    int i = 0; // charachter index
    int h = 0; // horizontal character placement
    int v = 0; // vertical character placement
    while(message[i] != 0){
        drawLetter(x+h, y+v, message[i]);
        sleep_ms(20); // add a delay for fun

        // check if next word will fit
        int left = (127 - h) / 6; // see how many more characters can fit
        for(int c = 1; c <= left; c++){ // look at the next characters that will fit on the line
            if(message[i+c] == ' '){ // if there is a space in there it's all good so continue to print
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
