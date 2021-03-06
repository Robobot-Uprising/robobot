#!/usr/bin/env python3

import evdev
from ev3dev.ev3 import *
import ev3dev.auto as ev3
import threading
import time

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
running = True

ts1 = TouchSensor('in1') 
ts2 = TouchSensor('in2')

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
        if event.code == 5:
            print("Stopping motor thread")



    if event.type == 1 and event.code == 302 and event.value == 1:
        print("X button is pressed. Stopping.")
        running = False
        time.sleep(0.5) # Wait for the motor thread to finish
        break
