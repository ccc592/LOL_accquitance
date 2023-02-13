import time

from ConfigUtils import my_config

from PIL import Image, ImageGrab
import os

class ImageUtils:
    def __init__(self):
        self.__image = None
        self.__image_grab = None
        self.__hero_top = tuple([int(x) for x in my_config.get("image_crop", "hero_top").split(',')])
        self.__player_top = tuple([int(x) for x in my_config.get("image_crop", "player_top").split(',')])
        self.__hero_bottom = tuple([int(x) for x in my_config.get("image_crop", "hero_bottom").split(',')])
        self.__player_bottom = tuple([int(x) for x in my_config.get("image_crop", "player_bottom").split(',')])

    def set_image(self):
        self.__image = Image.open("./resource/test1.png")

    def crop_image(self):
        self.set_image()
        cropped_image_hero_top = self.__image.crop(self.__hero_top)
        cropped_image_player_top = self.__image.crop(self.__player_top)
        cropped_image_hero_bottom = self.__image.crop(self.__hero_bottom)
        cropped_image_player_bottom = self.__image.crop(self.__player_bottom)

        images = [
            cropped_image_hero_top,
            cropped_image_player_top,
            cropped_image_hero_bottom,
            cropped_image_player_bottom,
        ]

        max_width = max(im.size[0] for im in images)
        total_height = sum(im.size[1] for im in images)

        finish_image = Image.new('RGBA', (max_width, total_height))

        y_offset = 0
        for im in images:
            finish_image.paste(im, (0, y_offset))
            y_offset += im.size[1]

        finish_image.save("./resource/finish_image.png")

    def screenshot(self):
        self.__image_grab = ImageGrab.grab(all_screens=False)
        self.__image_grab.save("./resource/screenshot.png")