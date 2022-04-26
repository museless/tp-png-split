#-*- coding: utf8 -*-

import os
import sys
import plistlib
import json

from tkinter import Tk, Button, filedialog
from tkinter.messagebox import showinfo

from PIL import Image


class BaseExporter:
    def load(self):
        pass

    def run(self, filename):
        path = filename.split(".")[0]
        exportpath = os.path.dirname(filename) + "/part"
        os.mkdir(exportpath)
        self.load(filename)
        self.img = Image.open(path + ".png")

        for k, v in self.frames.items():
            item = self.get_one_frame(v)
            self.export_image(self.img, exportpath + "/" + k + ".png", item)

        showinfo(title="提示", message="导出完成")


def PlistExporter(BaseExporter):
    def load(self, name):
        self.frames = plistlib.load(open(name, "rb"))["frames"]

    def export_image(self, img, pathname, item):
        # 去透明后的子图矩形
        x, y, w, h = tuple(map(int, item['frame']))
        # 子图原始大小
        size = tuple(map(int, item['sourceSize']))
        # 子图在原始图片中的偏移
        ox, oy, _, _ = tuple(map(int, item['sourceColorRect']))

        # 获取子图左上角，右下角
        if item['rotated']:
            box = (x, y, x + h, y + w)
        else:
            box = (x, y, x + w, y + h)

        # 使用原始大小创建图像，全透明
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        # 从图集中裁剪出子图
        sprite = img.crop(box)

        # rotated纹理旋转90度
        if item['rotated']:
            sprite = sprite.transpose(Image.ROTATE_90)

        # 粘贴子图，设置偏移
        image.paste(sprite, (ox, oy))

        # 保存到文件
        print('保存文件：%s' % pathname)
        image.save(pathname, 'png')

    def get_one_frame(self, frame):
        result = {}

        if frame['frame']:
            result['frame'] = frame['frame'].replace('}', '').replace('{', '').split(',')
            result['sourceSize'] = frame['sourceSize'].replace('}', '').replace('{', '').split(',')
            result['sourceColorRect'] = frame['sourceColorRect'].replace('}', '').replace('{', '').split(',')
            result['rotated'] = frame['rotated']

        return result


class JsonExporter(BaseExporter):
    def load(self, name):
        self.frames = json.load(open(name, "r", encoding="utf-8"))["frames"]

    def get_one_frame(self, frame):
        return frame

    def export_image(self, img, pathname, item):
        x, y, w, h = item["x"], item["y"], item["w"], item["h"]
        size = ( item["sourceW"], item["sourceH"] )
        ox, oy = item["offX"], item["offY"]

        image = Image.new('RGBA', size, (0, 0, 0, 0))
        sprite = img.crop((x, y, x + w, y + h))

        image.paste(sprite, (ox, oy))
        image.save(pathname, 'png')


def gen_image(filename):
    if filename.endswith(".json"):
        export = JsonExporter()
    else:
        export = PlistExporter()

    export.run(filename)


def pickfile():
    fname = filedialog.askopenfilename(
        title="请选择",
        filetypes=(
            ("Json file", "*.json"),
            ("Plist", "*.plist")
        )
    )

    fname and gen_image(fname)


def main(argv=sys.argv):
    top = Tk()
    top.title("图集还原")
    top.geometry("320x160")

    Button(top, text="选择plist/json文件", command=pickfile, anchor="c").pack()
    top.mainloop()


if __name__ == '__main__':
    main()

