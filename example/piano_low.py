# Require:
# 1.SD with 320*240 JPG Pic in /img/welcome/home.jpg, or you can change the image Path

import ulab as np
from sfgl import *
from machine import Timer,PWM
import time
from fpioa_manager import fm
import _thread

tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
ch = PWM(tim, freq=1, duty=50, pin=9)

def bind(status, **kwargs):
    if status == 1:
        print(1)
        ch.freq(kwargs["freq"])
        print(3)
    else:
        print(2)
        ch.freq(100000)



lcd.init()
ts.init()
background = image.Image("/sd/img/welcome/home.jpg")
Logo = image.Image("/sd/img/welcome/home.jpg")
renderer = FurryRenderer(background)
Do = FurryController.Button(Logo, x=10,y=30, alpha=100)
Do.setscale(0.2)
Do.setbind(bind)
Re = FurryController.Button(Logo, x=90,y=30, alpha=100)
Re.setscale(0.2)
Re.setbind(bind)
Me = FurryController.Button(Logo, x=170,y=30, alpha=100)
Me.setscale(0.2)
Me.setbind(bind)
Fa = FurryController.Button(Logo, x=250,y=30, alpha=100)
Fa.setscale(0.2)
Fa.setbind(bind)
So = FurryController.Button(Logo, x=10,y=100, alpha=100)
So.setscale(0.2)
So.setbind(bind)
La = FurryController.Button(Logo, x=90,y=100, alpha=100)
La.setscale(0.2)
La.setbind(bind)
Xi = FurryController.Button(Logo, x=170,y=100, alpha=100)
Xi.setscale(0.2)
Xi.setbind(bind)
Do2 = FurryController.Button(Logo, x=250,y=100, alpha=100)
Do2.setscale(0.2)
Do2.setbind(bind)
renderer.addcontroller(Do, "Do", 0)
renderer.addcontroller(Re, "Re", 0)
renderer.addcontroller(Me, "Me", 0)
renderer.addcontroller(Fa, "Fa", 0)
renderer.addcontroller(So, "So", 0)
renderer.addcontroller(La, "La", 0)
renderer.addcontroller(Xi, "Xi", 0)
renderer.addcontroller(Do2, "Do2", 0)
key = {"Do":{"freq": 523},"Re":{"freq": 583},"Me":{"freq": 659},"Fa":{"freq": 698},"So":{"freq": 784},"La":{"freq": 880},"Xi":{"freq": 988},"Do2":{"freq": 1046}}

while True:
    renderer.render(**key)
