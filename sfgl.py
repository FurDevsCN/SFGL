# Untitled - By: LEGION - 周四 10月 20 2022
import sensor, image, time, lcd
import touchscreen as ts
import os
import ulab as np
import gc
import _thread
THREAD_bindmap_processing = False
THREAD_bindmap =  []
THREAD_data = []
THREAD_ready = True
lock = _thread.allocate_lock()
class FurryController:
    class Basic:
        optimistic_render = False
        before_render = None
        after_render = None

        def _before_render(self, name, **kwargs):
            if self.before_render is not None:
                if kwargs is not None:
                    self.before_render(name, **kwargs)
                else:
                    self.before_render(name, {})

        def _after_render(self, name, **kwargs):
            if self.after_render is not None:
                if kwargs is not None:
                    self.after_render(name, **kwargs)
                else:
                    self.after_render(name, {})

        def _render(self, images, cotroller, message):
            return images



    class Pic(Basic):
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
                if self.bind is None:
                    return False
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
            sensor.reset(dual_buff=True)
            sensor.set_pixformat(sensor.RGB565) # 设置摄像头输出格式为 RGB565（也可以是GRAYSCALE）
            sensor.set_framesize(sensor.QVGA)   # 设置摄像头输出大小为 QVGA (320x240)
            sensor.skip_frames(time = 2000)     # 跳过2000帧
            self.image = sensor.snapshot()
            sensor.set_jb_quality(1)
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

    class Text(Basic):
        optimistic_render = True
        def __init__(self, text, x=0, y=0, scale=1, color=[255,255,255], alpha=100):
            self.text = text
            self.position = {'x': x, 'y': y}
            self.alpha = alpha
            self.scale = scale
            self.color = color
            self.click = False

        def _render(self, images, cotroller, message):
            if self.alpha == 0:
                return images
            images = images.draw_string(self.position['x'], self.position['y'], self.text, color=self.color, scale=self.scale)
            return images

        def x(self):
            return self.position['x']

        def y(self):
            return self.position['y']


def _calculate():
    global THREAD_data
    global THREAD_bindmap
    global THREAD_ready
    print("start")
    while True:
        try:
            lock.acquire()
            THREAD_ready = False
            tmp = np.zeros((240, 320), dtype=np.uint8)
            data = THREAD_data
            lock.release()
            for i in data:
                tmp[i[0]:i[1],i[2]:i[3]] = i[4]
            lock.acquire()
            THREAD_bindmap = tmp
            THREAD_ready = True
            lock.release()
            time.sleep(0.1)
        except Exception as e:
            THREAD_bindmap_processing = False
            _thread.exit()

class FurryRenderer:

    def __init__(self, images=None, width=320, height=240):
        global THREAD_bindmap
        if images is None:
            images = image.Image()
        self.uid = -1
        self.width = width
        self.height = height
        self.image = images
        self.control = []
        self.animate = []
        self.bindmap = np.zeros((height, width), dtype=np.uint8)
        THREAD_bindmap = self.bindmap
        self.press = False
        self.changemap = True
        lcd.init()

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
        global THREAD_bindmap_processing
        global THREAD_bindmap,THREAD_data
        global _thread
        self.bindmap = THREAD_bindmap
        # Get Touch Status
        t = time.ticks_us()
        (status,x,y) = ts.read()
        if self.press == False:
            if status != ts.STATUS_RELEASE and (x!=0 or y!=0) and y<self.height: # Button Unpress
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
             if status == ts.STATUS_RELEASE and (x!=0 or y!=0)and y<self.height: # Button Press
                uid = self.bindmap[y][x] - 1
                if uid != -1 and self.control[uid]["controller"].active:
                    name = self.control[uid]["name"]
                    kwa = kwargs.get(name)
                    if kwa is None:
                        self.control[uid]["controller"].release()
                    else:
                        self.control[uid]["controller"].release(**kwa)
                    self.press = False
        t = time.ticks_diff(time.ticks_us(), t)
        print("Get Touch Status USE " + str(t/1000) + " ms")
        # Set Status
        t = time.ticks_us()
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
        t = time.ticks_diff(time.ticks_us(), t)
        print("Animation USE " + str(t/1000) + " ms")
        # Render
        t = time.ticks_us()
        self.image.clear()
        tmp = self.control
        tmpp = sorted(tmp, key=lambda tmp: tmp["zindex"])
        step = 0
        data = []
        for i in tmpp:
            i["controller"]._before_render(i["name"])
            x = i["controller"].x()
            y = i["controller"].y()
            scale = i["controller"].scale
            alpha = int(i["controller"].alpha / 100 * 256)
            if alpha != 0  and not i["controller"].optimistic_render:
                self.image.draw_image(i["controller"].getimage(), x, y, x_scale=scale, y_scale=scale, alpha=alpha)
            if i["controller"].optimistic_render:
                self.image = i["controller"]._render(self.image, i["controller"], kwargs)
            if i["controller"].click:
                scale = i["controller"].scale
                w_s = max(0, x) # width start
                h_s = max(0, y) # height start
                h_e = min(239, int(h_s + scale * i["controller"].height()))
                w_e = min(319, int(w_s + scale * i["controller"].width()))
                data.append([h_s,h_e,w_s,w_e,i["uid"]+1])
            i["controller"]._after_render(i["name"])
        if THREAD_ready:
            lock.acquire()
            THREAD_data = data
            self.bindmap = THREAD_bindmap
            lock.release()
        if not THREAD_bindmap_processing:
            try:
                _thread.start_new_thread(_calculate, () )
                time.sleep(1)
            except:
                print("Error Retry")
            finally:
                THREAD_bindmap_processing = True

        t = time.ticks_diff(time.ticks_us(), t)
        print("Render USE " + str(t/1000) + " ms")
        self.changemap = not self.changemap
        t = time.ticks_us()
        lcd.display(self.image)
        t = time.ticks_diff(time.ticks_us(), t)
        print("LCD USE " + str(t/1000) + " ms")
