# SFGL
Simple Furry Graphics Library (For K210 - Micropython)
Create GUI for K210

# Example
    import sensor, image, time, lcd
    import touchscreen as ts
    import ulab as np
    import gc
    from sfgl import *


    def enter(status, **kwargs):
        global renderer
        if status == 0:
            renderer.setanimate("Furry",1, alpha=0)
            cam = FurryController.Camera(scale=0.25)
            renderer.destorycontroller("Furry")
            renderer.addcontroller(cam, "Camera", 0)
            renderer.setanimate("Camera",5, scale=1)
        else:
            print("Press")

    def test(name, **k):
        print(name)

    def welcome_main():
        global renderer
        lcd.init()
        ts.init()
        background = image.Image()
        Logo = image.Image().draw_string(100, 80, "SFGL \nCLICK TO CONTINUE", color=(200,0,0), scale=2)
        renderer = FurryRenderer(background)
        Logo = FurryController.Button(Logo, x=0,y=0, alpha=100)
        Logo._before_render = test
        Logo.setbind(enter)
        renderer.addcontroller(Logo, "Furry", 0)
        #renderer.setanimate("Furry",2,alpha=100)
        clock = time.clock()
        print(lcd.freq(20000000))
        for i in range(1000):
            clock.tick()
            renderer.render()
            time.sleep_ms(1)
            print(clock.fps())

    def main():
        # Set GC
        gc.enable()
        GCSIZE = 2 * 1024 * 1024
        if maix.utils.gc_heap_size() != GCSIZE:
            maix.utils.gc_heap_size(GCSIZE)
        # Set Cpu/Kpu
        # Start Up
        welcome_main()


    main()

# Constrcut
- FurryRenderer 
  - 
- FurryController
  - 
  - Pic  
  - Button
  - Camera
  - Text
  - Basic

# Function
SET TOUCHSCREEN -> SET ANIMATION -> before_render() -> RENDER -> after_render() -> GET TOUCHSTATUS -> SHOW ON LCD

# Optimistic Controller
1. Use Basic as Super Class
2. set "optimistic_render" as True
3. define _render(self,  images, cotroller, message) in your class
4. You can see "Text" Controller for example

