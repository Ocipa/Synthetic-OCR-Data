


from typing import Text

from numpy.random.mtrand import rand
from sodgen import config
from sodgen.config import Config
from sodgen.fonts import *

from math import floor, ceil

import random
import numpy as np



class image():
    def __init__(self, fonts: list, config: Config):
        assert isinstance(fonts, list), 'missing fonts, or fonts is not a list'
        assert isinstance(config, Config), 'config is not a Config object'

        self.fonts = fonts
        self.config = config

        self._build()
    
    def _build(self):
        width, height = self.config.size

        self.image = np.full((height, width, 3), fill_value=255, dtype=np.uint8)
        
        self.image = Image.fromarray(self.image, mode='RGB')

        '''
        do background stuff here
        '''

        self._draw_text()


    def _draw_text(self):
        font = random.choice(self.fonts)

        text = Text(font=font, config=self.config)
        center = text.get_center('00')

        draw = ImageDraw.Draw(self.image)
        draw.text(
            (0 - center[1], 0 - center[0]),
            '00',
            fill = text.font_fill,
            font = text.font.get_font(text.font_size),
            stroke_width = text.stroke_width,
            stroke_fill = text.stroke_fill,
            anchor = 'lt',
            spacing = 20,
        )

        draw.line([(128, 0), (128, 256)], fill=0, width=2)
        draw.line([(0, 128), (256, 128)], fill=0, width=2)

        self._draw_mask(text)

        
    
    def _draw_mask(self, text: Text):
        mask, offset = text.get_mask('00')
        height, width = mask.shape

        im_width, im_height = self.config.size

        pos = (random.randint(0, 256), random.randint(0, 256)) #x, y

        mask = mask[np.abs(np.clip((pos[1] - floor(height / 2)), -999, 0)):np.abs(pos[1] - im_height - ceil(height / 2))]
        mask = mask[:, np.abs(np.clip(pos[0] - floor(width / 2), -999, 0)):np.abs(pos[0] - im_width - ceil(width / 2))]

        new_height, new_width = mask.shape

        top_pad = np.clip(pos[1] - ceil(new_height / (2 / (height / new_height))), 0, im_height)
        bottom_pad = im_height - (top_pad + new_height)

        left_pad = np.clip(pos[0] - ceil(new_width / (2 / (width / new_width))), 0, im_width)
        right_pad = im_width - (left_pad + new_width)

        padded_mask = np.pad(mask, ((top_pad, bottom_pad), (left_pad, right_pad)))

        padded_mask = np.dstack((padded_mask, padded_mask, padded_mask))

        im1 = np.array(self.image)
        im2 = np.full((256, 256, 3), fill_value=128, dtype=np.uint8)

        self.image = np.where(padded_mask == 255, im2, im1)



