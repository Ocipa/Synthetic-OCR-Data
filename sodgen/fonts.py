
from sodgen.config import Config
import sodgen.color as color

import requests
session = requests.session()

from zipfile import ZipFile
from io import BytesIO

from PIL import Image, ImageFont, ImageDraw
import numpy as np
import random

from math import floor, ceil

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
    def __init__(self, text: str, font: font, config: Config):
        assert font, 'missing font_path'

        self.text = text

        self.font = font
        self.config = config

        self._build()

    def _build(self):
        self.font_size = random.randint(*self.config.font_size)
        self.stroke_width = random.randint(*self.config.stroke_width)

        self.font_fill = color.to_rgb(option=self.config.font_fill)
        self.stroke_fill = self.config.stroke_fill(self.font_fill)

        self.pos = (int(self.config.size[1] / 2), int(self.config.size[0] / 2))

        self.render = self._render()
        self.bbox = self._getbbox()
    
    def _render(self):
        render = np.full((self.config.size[1], self.config.size[0], 3), 0, dtype='int')
        im = Image.fromarray(render, mode='RGB')
        draw = ImageDraw.Draw(im)

        draw.multiline_text(
            xy = self.pos,
            text = self.text,
            fill = self.font_fill,
            font = self.font.get_font(size=self.font_size),
            anchor = 'mm',
            spacing = 4,
            align = 'left',
            direction = None,
            features = None,
            language = None,
            stroke_width = self.stroke_width,
            stroke_fill = self.stroke_fill,
            embedded_color = False
        )

        render = np.array(im)

        return render
    
    def _getbbox(self):
        a = self.render.nonzero()

        minx, maxx = np.min(a[1]), np.max(a[1])
        miny, maxy = np.min(a[0]), np.max(a[0])

        c0, c1 = (minx, miny), (maxx, maxy)

        return c0, c1

    def _render_mask(self):
        render = self.render.copy()

        m = np.clip(render, 0, 1, dtype='int') * 255

        return m
    
    def set_pos(self, texts: list=[]):
        pos = (random.randint(0, self.config.size[0]), random.randint(0, self.config.size[1]))
        pos_grid = np.full((self.config.size[1], self.config.size[0]), fill_value=0)

        force_inbounds = self.config.text_force_inbounds
        allow_overlap = self.config.text_overlap

        width = self.bbox[1][0] - self.bbox[0][0]
        height = self.bbox[1][1] - self.bbox[0][1]

        if force_inbounds:
            minx, maxx = int(width / 2), int(self.config.size[0] - width / 2)
            miny, maxy = int(height / 2), int(self.config.size[1] - height / 2)

            pos_grid[miny:maxy, minx:maxx] = 1
        
        if not allow_overlap:
            for i in texts:
                i_width = i.bbox[1][0] - i.bbox[0][0]
                i_height = i.bbox[1][1] - i.bbox[0][1]

                i_minx = np.clip(int(i.pos[0] - i_width / 2 - width / 2), 0, self.config.size[0])
                i_maxx = np.clip(int(i.pos[0] + i_width / 2 + width / 2), 0, self.config.size[0])

                i_miny = np.clip(int(i.pos[1] - i_height / 2 - height / 2), 0, self.config.size[1])
                i_maxy = np.clip(int(i.pos[1] + i_height / 2 + height / 2), 0, self.config.size[1])

                pos_grid[i_miny:i_maxy, i_minx:i_maxx] = 0

        
        num_nonzero = np.count_nonzero(pos_grid)
        if num_nonzero > 0:
            nonzero_y, nonzero_x = pos_grid.nonzero()
            rint = np.random.randint(0, len(nonzero_y))
            pos = (nonzero_x[rint], nonzero_y[rint])

            self.pos = pos

            self.render = self._render()
            self.bbox = self._getbbox()
        else:
            self.pos = None



    
    # def set_pos(self, texts: list=[]):
    #     pos = (random.randint(0, self.config.size[0]), random.randint(0, self.config.size[1]))
    #     pos_grid = np.full(self.config.size, fill_value=0)

    #     force_inbounds = self.config.text_force_inbounds
    #     allow_overlap = self.config.text_overlap

    #     mask, offset = self.get_mask(self.text)
    #     text_height, text_width = mask.shape

    #     minx, maxx = int(text_width / 2), int(self.config.size[0] - text_width / 2)
    #     miny, maxy = int(text_height / 2), int(self.config.size[1] - text_height / 2)

    #     if force_inbounds:
    #         pos_grid[miny:maxy, minx:maxx] = 1


    #     if not allow_overlap:
    #         for i in texts:
    #             i_mask, i_offset = i.get_mask(i.text)
    #             i_text_height, i_text_width = i_mask.shape

    #             i_minx = np.clip(int(i.pos[0] - i_text_width / 2 - text_width / 2), 0, self.config.size[0])
    #             i_maxx = np.clip(int(i.pos[0] + i_text_width / 2 + text_width / 2), 0, self.config.size[0])

    #             i_miny = np.clip(int(i.pos[1] - i_text_height / 2 - text_height / 2), 0, self.config.size[1])
    #             i_maxy = np.clip(int(i.pos[1] + i_text_height / 2 + text_height / 2), 0, self.config.size[1])

    #             pos_grid[i_miny:i_maxy, i_minx:i_maxx] = 0

    #     num_nonzero = np.count_nonzero(pos_grid)
    #     if num_nonzero > 0:
    #         nonzero_y, nonzero_x = pos_grid.nonzero()
    #         rint = np.random.randint(0, len(nonzero_y))
    #         pos = (nonzero_x[rint], nonzero_y[rint])

    #         self.pos = pos
    #     else:
    #         self.pos = None
    
    # def get_center(self, text: str):
    #     f = self.font.get_font(size=self.font_size)

    #     left, top, right, bottom = f.getbbox(text=text, anchor='la')

    #     return ((bottom + top) / 2, (right + left) / 2)

    
    # def get_mask(self, text):
    #     f = self.font.get_font(size= self.font_size)

    #     size = f.getsize(text)
    #     padded_size = (size[0] + self.stroke_width * 2, size[1] + self.stroke_width * 2)

    #     mask, offset = f.getmask2(text, anchor='la')
    #     padded_mask, padded_offset = f.getmask2(text, stroke_width=self.stroke_width, anchor='la')

    #     mask_arr = np.pad(np.array(mask).reshape(int(len(mask) / size[0]), size[0]), self.stroke_width)
    #     padded_mask_arr = np.array(padded_mask).reshape(int(len(padded_mask) / padded_size[0]), padded_size[0])

    #     m = np.clip(np.add(mask_arr, padded_mask_arr), 0, 1, dtype='int') * 255

    #     return (m, offset)
