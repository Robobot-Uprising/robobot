#!/usr/bin/env python3

import evdev
from ev3dev.ev3 import *
import ev3dev.auto as ev3
import threading
import time
from evaluateLine import evaluate

## Some helpers ##
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def scale(val, src, dst):
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def scale_stick(value):
    return scale(value,(0,255),(-1000,1000))

def dc_clamp(value):
    return clamp(value,-1000,1000)

## Initializing ##
print("Finding ps3 controller...")
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
for device in devices:
    if device.name == 'PLAYSTATION(R)3 Controller':
        ps3dev = device.fn

gamepad = evdev.InputDevice(ps3dev)

forward_speed = 0
side_speed = 0
clamp_speed = 0
clamp_sidespeed = 0
color_speed = 0
running = True

class MotorThread(threading.Thread):
    def __init__(self):
        self.right_motor = ev3.LargeMotor(ev3.OUTPUT_A)
        self.left_motor = ev3.LargeMotor(ev3.OUTPUT_D)
        threading.Thread.__init__(self)

    def run(self):
        print("Engine running!")
        while running:
            self.right_motor.run_forever(speed_sp=dc_clamp(forward_speed+side_speed))
            self.left_motor.run_forever(speed_sp=dc_clamp(-forward_speed+side_speed))

        self.right_motor.stop()
        self.left_motor.stop()


motor_thread = MotorThread()
motor_thread.setDaemon(True)
motor_thread.start()

class clawMotorThread(threading.Thread):
    def __init__(self):
        self.claw_motor = ev3.MediumMotor(ev3.OUTPUT_B)
        threading.Thread.__init__(self)
    
    def run(self):
        print("Claw Activated!")
        while running:

            self.claw_motor.run_forever(speed_sp=dc_clamp(clamp_speed+clamp_sidespeed))
        
        self.claw_motor.stop()

claw_motor_thread = clawMotorThread()
claw_motor_thread.setDaemon(True)
claw_motor_thread.start()


color_sensor = ColorSensor()
color_sensor.mode = 'COL-COLOR'

for event in gamepad.read_loop():   
    if event.type == 3:
        if event.code == 0:         
            forward_speed = -scale_stick(event.value)
        if event.code == 1:         
            side_speed = -scale_stick(event.value)
        if side_speed < 100 and side_speed > -100:
            side_speed = 0
        if forward_speed < 100 and forward_speed > -100:
            forward_speed = 0
        if event.code == 4:
            clamp_speed = -scale_stick(event.value)
        if event.code == 3:
            clamp_sidespeed = -scale_stick(event.value)
        if clamp_speed < 100 and forward_speed > -100:
            clamp_speed = 0
        if event.code == 5:
            forward_speed = evaluate(color_sensor)
            # if colors[colorSensor.value()] == 'white':
            #     print('Color is pressed')
            #     forward_speed = 200
            # else:
            #     print('it not white')
            #     forward_speed = 0

            #color_speed = -scale_stick(event.value)

