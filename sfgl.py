# Untitled - By: LEGION - 周四 10月 20 2022
import sensor, image, time, lcd
import touchscreen as ts
import os
import ulab as np
import gc

class FurryController:
    class Pic:
        def __init__(self, image, x=0, y=0, alpha=100):
            position = {'x': x, 'y': y}
            self.image = image
            self.position = position
            self.alpha = alpha
            self.scale = 1
            self.click = False

        def x(self):
            return self.position['x']

        def y(self):
            return self.position['y']

        def width(self):
            return self.image.width()

        def height(self):
            return self.image.height()

        def setposition(self, position=None, x=None, y=None):
            if x is not None:
                self.position['x'] = x
            if y is not None:
                self.position['y'] = y
            return self.position

        def resetpic(self, path):
            self.image = image.Image(path)
            return self.image

        def setalpha(self, alpha):
            self.alpha = alpha
            return self.alpha

        def getscale(self):
            return self.scale

        def setscale(self, scale):
            self.scale = scale
            return self.scale

        def getimage(self):
            return self.image




    class Button(Pic):
        def __init__(self, image, x=0, y=0, alpha=100, bind=None):
            super().__init__(image, x=x, y=y, alpha=alpha)
            self.bind = bind
            self.active = True
            self.click = True

        def setbind(self, bind):
            self.bind = bind
            return True

        def onclick(self, **kwargs):
            if self.active:
                if kwargs == {}:
                    return self.bind(1)
                else:
                    return self.bind(1, **kwargs)
            else:
                return False

        def release(self, **kwargs):
            if kwargs  == {}:
                return self.bind(0)
            else:
                return self.bind(0, **kwargs)

        def disable(self):
            self.active = False
            return True

        def able(self):
            self.active = True
            return True

    class Camera(Button):
        def __init__(self, x=0, y=0, alpha=100, scale=1):
            sensor.reset()
            sensor.set_pixformat(sensor.RGB565) # 设置摄像头输出格式为 RGB565（也可以是GRAYSCALE）
            sensor.set_framesize(sensor.QVGA)   # 设置摄像头输出大小为 QVGA (320x240)
            sensor.skip_frames(time = 10)     # 跳过2000帧
            self.image = sensor.snapshot()
            sensor.set_jb_quality(10)
            self.position = {'x': x, 'y': y}
            self.alpha = alpha
            self.scale = scale
            self.click = False
            self.bind = None
            self.active = False
        def getimage(self):
            self.image = sensor.snapshot()
            return self.image
        instance = None
        def __new__(cls, *args, **kwargs):


            if cls.instance is None:

                cls.instance = super().__new__(cls)

            return cls.instance


class FurryRenderer:

    def __init__(self, image, width=320, height=240):
        self.uid = -1
        self.width = width
        self.height = height
        self.image = image
        self.control = []
        self.animate = []
        self.bindmap = np.zeros((height, width), dtype=np.uint8)
        self.press = False

    def addcontroller(self, controller: FurryController.Pic, name, zindex=0):
        self.uid += 1
        self.control.append({"controller": controller, "name": name, "zindex": zindex, "uid": self.uid})
        return self.control

    def destorycontroller(self, name):
        tmp = []
        for i in self.control:
            if i["name"] != name:
                tmp.append(i)
            else:
                del i["controller"]
        self.control = tmp
        return self.control

    def setanimate(self, name, times, x=0, y=0, scale=1, alpha=100):
        tmp = []
        for i in self.control:
            if i["name"] == name:
                tmp = i["controller"]
                break
        if not tmp:
            return False

        self.animate.append({
            "name": name,
            "time": times * 1000,
            "x": x,
            "y": y,
            "a": alpha,
            "scale": scale,
            "from": time.ticks_ms(),
            "f_x": tmp.x(),
            "f_y": tmp.y(),
            "f_s": tmp.scale,
            "f_a": tmp.alpha,
            "controller": tmp
        })

        return True

    def stopanimate(self, name):
        tmp = []
        for i in self.animate:
            if i["name"] != name:
                tmp.append(i)
        self.animate = tmp

    def render(self, **kwargs):
        # Get Touch Status
        (status,x,y) = ts.read()
        if self.press == False:
            if status != ts.STATUS_RELEASE and (x!=0 or y!=0):
                uid = self.bindmap[y][x] - 1
                if uid != -1 and self.control[uid]["controller"].active:
                    name = self.control[uid]["name"]
                    print(name)
                    kwa = kwargs.get(name)
                    if kwa is None:
                        self.control[uid]["controller"].onclick()
                    else:
                        self.control[uid]["controller"].onclick(**kwa)
                    self.press = True
        else:
             if status == ts.STATUS_RELEASE and (x!=0 or y!=0):
                uid = self.bindmap[y][x] - 1
                if uid != -1 and self.control[uid]["controller"].active:
                    name = self.control[uid]["name"]
                    kwa = kwargs.get(name)
                    if kwa is None:
                        self.control[uid]["controller"].release()
                    else:
                        self.control[uid]["controller"].release(**kwa)
                    self.press = False
        # Set Status
        self.bindmap[:, :] = 0
        for i in self.animate:
            t = time.ticks_ms()
            proc = (t - i["from"]) / i["time"]
            if t - i["from"] > i["time"]:
                self.stopanimate(i["name"])
                proc = 1
            x = int(i["x"] * proc) + i["f_x"]
            y = int(i["y"] * proc) + i["f_y"]
            i["controller"].setposition(x=x, y=y)
            s_t = (i["scale"] / i["f_s"]) - 1
            i["controller"].setscale(((s_t * proc) + 1) * i["f_s"])
            f_a = (i["a"] - i["f_a"]) * proc + i["f_a"]
            i["controller"].setalpha(int(f_a))

        # Render
        self.image.clear()
        tmp = self.control
        tmpp = sorted(tmp, key=lambda tmp: tmp["zindex"])
        step = 0
        for i in tmpp:
            x = i["controller"].x()
            y = i["controller"].y()
            scale = i["controller"].getscale()
            alpha = int(i["controller"].alpha / 100 * 256)
            if alpha != 0:
                self.image.draw_image(i["controller"].getimage(), x, y, x_scale=scale, y_scale=scale, alpha=alpha)
            if i["controller"].click:
                w_s = max(0, x)
                h_s = max(0, y)
                h_e = min(239, int(h_s + scale * i["controller"].height()))
                w_e = min(319, int(w_s + scale * i["controller"].width()))
                self.bindmap[h_s:h_e, w_s:w_e] = step + 1
            step += 1
        lcd.display(self.image)
