# -*- coding:utf-8 -*-

import os
import numpy
import time
import subprocess
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
from matplotlib.animation import FuncAnimation

need_update = True


class WechatJump(object):
    def get_screen_image(self):
        # 手机截图
        process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
        # 获取截图二进制内容
        screenshot = process.stdout.read()
        # 格式化,安卓和windows
        screenshot = screenshot.replace(b'\r\n', b'\n')
        # 把截图存到内存
        img_fb = BytesIO()
        img_fb.write(screenshot)
        return numpy.array(Image.open(img_fb))

    # 跳到下一块
    def jump_to_next(self, point1, point2):
        # 计算弦的长度
        x1,y1 = point1;x2,y2 = point2
        distance = ((x2-x1)**2 + (y2-y1)**2)**0.5
        os.system('adb shell input swipe 320 410 320 410 {}'.format(int(distance*1.35)))

    # 绑定鼠标单击事件
    def on_calck(self, event, coor=[]): # event是点击事件的坐标位置
        global need_update
        coor.append((event.xdata,event.ydata))
        if len(coor) == 2:
            self.jump_to_next(coor.pop(), coor.pop())
        need_update = True

    # 更新图片
    def update_screen(self, frame):
        global need_update
        if need_update == True:
            time.sleep(1)
            self.axes_image.set_array(self.get_screen_image())
            need_update = False
        return self.axes_image,

    def main(self):
        # 创建一个空白的图片对象
        figure = plt.figure()
        # 把获取的图片画在坐标轴上
        self.axes_image = plt.imshow(self.get_screen_image(), animated=True)
        # 绑定鼠标单击事件
        figure.canvas.mpl_connect('button_press_event', self.on_calck)
        # 更新图片
        ani = FuncAnimation(figure, self.update_screen, interval=100, blit=True)
        plt.show()

if __name__ == '__main__':
    wechat_jump = WechatJump()
    wechat_jump.main()
