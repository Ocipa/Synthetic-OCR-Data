
from sodgen.config import Config
import sodgen.color as color
from sodgen.utility import rotate_bbox

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

        rotation = self.config.text_rotation
        self.text_rotation = int(rotation) if isinstance(rotation, (int, float)) else random.choice(rotation)

        align = self.config.text_align
        self.text_align = align if isinstance(align, str) else random.choice(align)

        spacing = self.config.line_spacing
        self.line_spacing = spacing if isinstance(spacing, (int, float)) else random.randint(*spacing)

        self.direction = None

        self.features = None

        self.language = None

        self.embedded_color = None

        self.pos = (int(self.config.size[1] / 2), int(self.config.size[0] / 2))

        self.render_offset = (0, 0)
        self.render_offset2 = (0, 0)
        self.render = self._render()
        self.render_size = self.render.shape[1::-1]
    
    def _render(self):
        render = np.full((self.config.size[1], self.config.size[0], 4), 0, dtype='uint8')
        im = Image.fromarray(render, mode='RGBA')
        draw = ImageDraw.Draw(im)

        widths = []
        max_width = 0

        lines = self.text.split('\n')
        line_spacing = (draw.textsize("A", font=self.font.get_font(size=self.font_size), stroke_width=self.stroke_width)[1] + self.line_spacing)

        for line in lines:
            line_width = draw.textlength(line, self.font.get_font(size=self.font_size), direction=self.direction, features=self.features, language=self.language)
            widths.append(line_width)
            max_width = max(max_width, line_width)
        
        top = self.pos[1] - (len(lines) - 1) * line_spacing / 2.0

        self.lines_bbox = []

        for i, v in enumerate(lines):
            left = self.pos[0]
            width_difference = max_width - widths[i]

            if self.text_align == 'left':
                left -= width_difference / 2.0
            elif self.text_align == 'right':
                left += width_difference / 2.0
            
            draw.text(
                xy = (left, top),
                text = v,
                fill = self.font_fill,
                font = self.font.get_font(size=self.font_size),
                anchor = 'mm',
                spacing = self.line_spacing,
                align = self.text_align,
                direction = self.direction,
                features = self.features,
                language = self.language,
                stroke_width = self.stroke_width,
                stroke_fill = self.stroke_fill,
                embedded_color = self.embedded_color
            )

            bbox = draw.textbbox(
                xy = (left, top),
                text = v,
                font = self.font.get_font(size=self.font_size),
                anchor = 'mm',
                spacing = self.line_spacing,
                align = self.text_align,
                direction = self.direction,
                features = self.features,
                language = self.language,
                stroke_width = self.stroke_width,
                embedded_color = self.embedded_color 
            )

            c0 = (bbox[0] - self.pos[0], bbox[1] - self.pos[1])
            c1 = (bbox[2] - self.pos[0], bbox[1] - self.pos[1])
            c2 = (bbox[2] - self.pos[0], bbox[3] - self.pos[1])
            c3 = (bbox[0] - self.pos[0], bbox[3] - self.pos[1])

            bbox = [c0, c1, c2, c3]
            bbox = rotate_bbox(bbox, (0, 0), self.text_rotation)

            self.lines_bbox.append(bbox)

            top += line_spacing

        im = im.rotate(self.text_rotation, fillcolor=0)
        a = np.array(im).nonzero()
        
        minx, maxx = np.min(a[1]), np.max(a[1])
        miny, maxy = np.min(a[0]), np.max(a[0])

        self.render_offset = (minx - self.pos[0], miny - self.pos[1])
        self.render_offset2 = (maxx - self.pos[0], maxy - self.pos[1])

        im = im.crop((minx, miny, maxx, maxy))
        render = np.array(im)

        return render
    
    # def _getbbox(self):
    #     a = self.render.nonzero()

    #     minx, maxx = np.min(a[1]), np.max(a[1])
    #     miny, maxy = np.min(a[0]), np.max(a[0])

    #     c0, c1 = (minx, miny), (maxx, maxy)

    #     return c0, c1

    def _render_mask(self):
        render = self.render.copy()

        m = np.clip(render, 0, 1, dtype='int') * 255

        return m
    
    def set_pos(self, texts: list=[]):
        pos = (random.randint(0, self.config.size[0]), random.randint(0, self.config.size[1]))
        pos_grid = np.full((self.config.size[1], self.config.size[0]), fill_value=0)

        force_inbounds = self.config.text_force_inbounds
        allow_overlap = self.config.text_overlap

        w1, w2 = (-self.render_offset[0], self.render_offset2[0])
        h1, h2 = (-self.render_offset[1], self.render_offset2[1])

        if force_inbounds:
            minx, maxx = int(w1), int(self.config.size[0] - w2)
            miny, maxy = int(h1), int(self.config.size[1] - h2)

            pos_grid[miny:maxy, minx:maxx] = 1
        
        if not allow_overlap:
            for i in texts:
                i_w1, i_w2 = (-i.render_offset[0], i.render_offset2[0])
                i_h1, i_h2 = (-i.render_offset[1], i.render_offset2[1])

                i_minx = np.clip(int(i.pos[0] - i_w1 - w2), 0, self.config.size[0])
                i_maxx = np.clip(int(i.pos[0] + i_w2 + w1), 0, self.config.size[0])

                i_miny = np.clip(int(i.pos[1] - i_h1 - h2), 0, self.config.size[1])
                i_maxy = np.clip(int(i.pos[1] + i_h2 + h1), 0, self.config.size[1])

                pos_grid[i_miny:i_maxy, i_minx:i_maxx] = 0

        
        num_nonzero = np.count_nonzero(pos_grid)
        if num_nonzero > 0:
            nonzero_y, nonzero_x = pos_grid.nonzero()
            rint = np.random.randint(0, len(nonzero_y))
            pos = (nonzero_x[rint], nonzero_y[rint])

            self.pos = pos

            for i, v in enumerate(self.lines_bbox):
                c0, c1, c2, c3 = v

                c0 = (c0[0] + self.pos[0], c0[1] + self.pos[1])
                c1 = (c1[0] + self.pos[0], c1[1] + self.pos[1])
                c2 = (c2[0] + self.pos[0], c2[1] + self.pos[1])
                c3 = (c3[0] + self.pos[0], c3[1] + self.pos[1])

                self.lines_bbox[i] = [c0, c1, c2, c3]
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
