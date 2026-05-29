import serial
ser = serial.Serial('COM3') # the name of your port here
print('Opening port: ' + str(ser.name))
import pygame
import pgzrun

WIDTH = 600
HEIGHT = 600
n1_int = 0
n2_int = 0
def update():
   n_bytes = ser.readline() # read all the letters available
   s = str(n_bytes) # turn them into a str
   result = [int(x) for x in s[s.find('(')+1:s.find(')')].split(',')]
   global up1, down1, up2, down2
   up1 = result[0]
   down1 = result[1]
   up2 = result[2]
   down2 = result[3]

def draw():
   screen.fill((0, 0, 0))
   screen.draw.text('up1: ' + str(up1)+ '\n' + 'down1: ' + str(down1)+ '\n' + 'up2: ' + str(up2)+ '\n' + 'down2: ' + str(down2),(0, 0))

pgzrun.go()