
from sodgen.config import Config
import sodgen.color as color
from sodgen.utility import rotate_bbox, translate_bbox, extrema_from_points, extra_bytes, config_value_to_value

import requests
session = requests.session()

from zipfile import ZipFile
from io import BytesIO

import skia # type: ignore
import numpy as np
import random

import os



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

        fonts.append(f)
    
    return fonts


class font:
    def __init__(self, path):
        self.path = path
    
    def get(self, size: int=10):
        f = skia.Font(skia.Typeface.MakeFromFile(self.path), size)
        
        return f

class Text:
    def __init__(self, text: str, font: font, config: Config):
        assert font, 'missing font_path'

        self.text = text
        self.config = config

        self.font_size = config_value_to_value(self.config.font_size)
        self.stroke_width = config_value_to_value(self.config.stroke_width)

        self.font = font.get(self.font_size)

        self._build()

    def _build(self):
        # TODO: move everything in _build to __init__ ??
        self.font_fill = color.to_rgb(option=self.config.font_fill)
        self.stroke_fill = self.config.stroke_fill(self.font_fill)

        self.text_rotation = config_value_to_value(self.config.text_rotation)
        self.text_align = config_value_to_value(self.config.text_align)

        self.line_spacing = config_value_to_value(self.config.line_spacing)
        self.char_spacing_mult = config_value_to_value(self.config.char_spacing_mult)

        self.direction = None
        self.features = None
        self.language = None
        self.embedded_color = None

        self.pos = (0, 0)

        # NOTE: skia.ColorSetRGB seems to actually be BGR, so
        # the colors get reversed, if this gets fixed in the
        # skia library, then remove the [::-1]
        self.fill_paint = skia.Paint(
            AntiAlias=True,
            Color=skia.ColorSetRGB(*self.font_fill[::-1]),
            Style=skia.Paint.kFill_Style
        )

        self.stroke_paint = None
        if self.stroke_width > 0:
            # NOTE: skia.ColorSetRGB seems to actually be BGR, so
            # the colors get reversed, if this gets fixed in the
            # skia library, then remove the [::-1]
            self.stroke_paint = skia.Paint(
                AntiAlias=True,
                Color=skia.ColorSetRGB(*self.stroke_fill[::-1]),
                Style=skia.Paint.kStrokeAndFill_Style,
                StrokeWidth = self.stroke_width
            )

        self.render_offset = (0, 0)
        self.render_offset2 = (0, 0)

        self.bbox = self._calc_bbox()
    
    def _calc_bbox(self):
        '''
        
        '''
        metrics = self.font.getMetrics()
        line_spacing = (self.font.getSpacing() - metrics.fDescent)

        widths = []
        max_width = 0

        lines = self.text.split('\n')

        for line in lines:
            line_width = self.font.measureText(line, paint=self.fill_paint)
            widths.append(line_width)
            max_width = max(max_width, line_width)
        
        top = 0 - (len(lines)) * line_spacing / 2 + line_spacing

        lines_bbox = []
        
        for i, line in enumerate(lines):
            left = -max_width / 2
            width_difference = max_width - widths[i]

            if self.text_align == 'center':
                left += width_difference / 2.0
            elif self.text_align == 'right':
                left += width_difference


            glyphs = self.font.textToGlyphs(line)

            positions = self.font.getPos(glyphs, origin=(0, 0))
            
            for i, v in enumerate(positions):
                x, y = v

                positions[i].set(x * self.char_spacing_mult, y)

            sizes = self.font.getBounds(glyphs, self.stroke_paint if self.stroke_width > 0 else self.fill_paint)

            minx = list(positions[0])[0] + list(sizes[0])[0] + left
            maxx = list(positions[-1])[0] + list(sizes[-1])[2] + left

            miny = min([list(i)[1] for i in sizes]) + top
            maxy = max([list(i)[3] for i in sizes]) + top

            c0 = (minx, miny)
            c1 = (maxx, miny)
            c2 = (maxx, maxy)
            c3 = (minx, maxy)

            bbox = [c0, c1, c2, c3]
            bbox = rotate_bbox(bbox, (0, 0), self.text_rotation)

            lines_bbox.append(bbox)

            top += line_spacing
        
        return lines_bbox
    
    def render_text(self, canvas):
        '''
        
        '''
        metrics = self.font.getMetrics()
        line_spacing = (self.font.getSpacing() - metrics.fDescent)

        widths = []
        max_width = 0

        lines = self.text.split('\n')

        for line in lines:
            line_width = self.font.measureText(line, paint=self.fill_paint)
            widths.append(line_width)
            max_width = max(max_width, line_width)
        
        top = self.pos[1] - (len(lines)) * line_spacing / 2 + line_spacing

        if self.text_rotation != 0:
            canvas.rotate(-self.text_rotation, *self.pos)
        
        for i, line in enumerate(lines):
            left = self.pos[0] - max_width / 2
            width_difference = max_width - widths[i]

            if self.text_align == 'center':
                left += width_difference / 2.0
            elif self.text_align == 'right':
                left += width_difference

            glyphs = self.font.textToGlyphs(line)
            positions = self.font.getPos(glyphs, origin=(0, 0))

            # NOTE: skia-python has a bug (#153 github issue) where it assumes all characters
            # are 1 byte like english, but languages like chinese are 3 bytes per character.
            # if this is patched, then replace this try except with the code inside of
            # the try.
            try:
                xform = [
                    *[skia.RSXform.MakeFromRadians(1, 0, i.fX * self.char_spacing_mult, i.fY, 0, 0) for i in positions]
                ]

                blob = skia.TextBlob.MakeFromRSXform(line, xform, self.font, skia.TextEncoding.kUTF8)

            except RuntimeError:
                eb = extra_bytes(line)

                xform = [
                    *[skia.RSXform.MakeFromRadians(1, 0, i.fX * self.char_spacing_mult, i.fY, 0, 0) for i in positions],
                    *[skia.RSXform.MakeFromRadians(1, 0, 0, 0, 0, 0) for i in range(eb)]
                ]

                blob = skia.TextBlob.MakeFromRSXform(line, xform, self.font, skia.TextEncoding.kUTF8)

            if self.stroke_width > 0:
                canvas.drawTextBlob(blob, left, top, self.stroke_paint)
            canvas.drawTextBlob(blob, left, top, self.fill_paint)

            top += line_spacing
        
        if self.text_rotation != 0:
            canvas.rotate(self.text_rotation, *self.pos)

    
    def find_pos(self, texts: list=[]):
        '''
        
        '''
        pos = (random.randint(0, self.config.size[0]), random.randint(0, self.config.size[1]))
        pos_grid = np.full((self.config.size[1], self.config.size[0]), fill_value=0)

        force_inbounds = self.config.text_force_inbounds
        allow_overlap = self.config.text_overlap

        (minx, miny), (maxx, maxy) = translate_bbox(extrema_from_points(self.bbox), (-self.pos[0], -self.pos[1]))

        if force_inbounds:
            pos_grid[abs(miny):self.config.size[1] - maxy, abs(minx):self.config.size[0] - maxx] = 1
        
        if not allow_overlap:
            for i in texts:
                if i is self:
                    continue

                (i_w1, i_h1), (i_w2, i_h2) = translate_bbox(extrema_from_points(i.bbox), (-i.pos[0], -i.pos[1]))

                i_minx = np.clip(i.pos[0] - maxx + i_w1, 0, self.config.size[0])
                i_maxx = np.clip(i.pos[0] - minx + i_w2, 0, self.config.size[0])

                i_miny = np.clip(i.pos[1] - maxy + i_h1, 0, self.config.size[1])
                i_maxy = np.clip(i.pos[1] - miny + i_h2, 0, self.config.size[1])

                pos_grid[i_miny:i_maxy, i_minx:i_maxx] = 0



        num_nonzero = np.count_nonzero(pos_grid)
        if num_nonzero > 0:
            nonzero_y, nonzero_x = pos_grid.nonzero()
            rint = np.random.randint(0, len(nonzero_y))
            pos = (nonzero_x[rint], nonzero_y[rint])

            new_bbox = translate_bbox(self.bbox, (-self.pos[0], -self.pos[1]))

            self.pos = pos
            self.bbox = translate_bbox(new_bbox, self.pos)
        else:
            self.pos = None
            self.bbox = None

