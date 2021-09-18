
from os import error
from sys import is_finalizing

from sodgen.config import Config
import sodgen.color as color

import requests
from requests.models import MissingSchema
session = requests.session()

from zipfile import ZipFile
from io import BytesIO

from PIL import Image, ImageFont, ImageDraw
import numpy as np
import random

import os
# import sys
# sys.path.append('../')



def download_fonts_dir(path: str, download_link: str=None):
    '''
    downlaods fonts_dir from donwload_link

    ---
    path: path to download to eg. './fonts_dir'
    download_link: link to downlaod fonts_dir from

    ---
    -> return: None
    '''
    assert isinstance(path, str), 'Invalid path'

    if not download_link:
        # dropbox folder containing fonts
        download_link = 'https://www.dropbox.com/sh/u8isqbel4h8wopm/AADvZRJsubsfVh18ZOu45f2Ka?dl=1'
    
    response = session.get(download_link)
    zipped = ZipFile(BytesIO(response.content))
    zipped.extractall(path=path)


def get_fonts_from_dir(path: str, lang: str) -> list:
    '''
    creates a font object for each font in path (font_dir)

    ---
    path: path to font_dir
    lang: a valid language code

    ---
    -> return: a list of font objects
    '''
    fonts = []

    assert isinstance(path, str) and os.path.isdir(path), f'{path} is not a valid path to fonts_dir'

    assert isinstance(lang, str), f'{lang} is not a valid language code'

    font_dir = os.path.join(path, lang)
    assert os.path.isdir(font_dir), f'{lang} is not found in fonts_dir'

    for i in os.listdir(font_dir):
        f = font(os.path.join(path, lang, i))

        if f.valid:
            fonts.append(f)
    
    return fonts


class font:
    def __init__(self, path):
        self.path = path

        self.valid = self._is_valid()

    def _is_valid(self):
        '''
        checks if path to a font is valid by created a temporary PIL FreeTypeFont
        '''
        try:
            self.get_font()
            return True

        except OSError:
            return False
        
        return False
    
    def get_font(self, size: int=0):
        f = ImageFont.FreeTypeFont(self.path, size=size)

        return f

class Text:
    def __init__(self, font: font, config: Config):
        assert font, 'missing font_path'

        self.font = font
        self.config = config

        self._build()

    def _build(self):
        self.font_size = random.randint(*self.config.font_size)
        self.stroke_width = random.randint(*self.config.stroke_width)

        self.font_fill = color.to_rgb(option=self.config.font_fill)
        self.stroke_fill = self.config.stroke_fill(self.font_fill)
    
    def get_center(self, text: str):
        f = self.font.get_font(size=self.font_size)

        left, top, right, bottom = f.getbbox(text=text, anchor='lt')

        #return (int((bottom - top) / 2), int((right - left) / 2))

        size = f.getsize(text)

        return (int((bottom - top) / 2), int(size[0] / 2))

    
    def get_mask(self, text):
        f = self.font.get_font(size= self.font_size)

        size = f.getsize(text)
        padded_size = (size[0] + self.stroke_width * 2, size[1] + self.stroke_width * 2)

        mask, offset = f.getmask2(text, anchor='lt')
        padded_mask, padded_offset = f.getmask2(text, stroke_width=self.stroke_width, anchor='lt')

        mask_arr = np.pad(np.array(mask).reshape(int(len(mask) / size[0]), size[0]), self.stroke_width)
        padded_mask_arr = np.array(padded_mask).reshape(int(len(padded_mask) / padded_size[0]), padded_size[0])

        m = np.clip(np.add(mask_arr, padded_mask_arr), 0, 1, dtype='int') * 255

        return (m, offset)






