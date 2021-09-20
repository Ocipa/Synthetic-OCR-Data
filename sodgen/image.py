


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

        self.texts = []

        self._build()
    
    def _build(self):
        width, height = self.config.size

        self.image = np.full((height, width, 3), fill_value=255, dtype=np.uint8)
        
        self.image = Image.fromarray(self.image, mode='RGB')

        '''
        do background stuff here
        '''


        self.target_text_number = self.config.target_text_number
        if isinstance(self.target_text_number, tuple):
            self.target_text_number = random.randint(*self.target_text_number)
        
        for i in range(self.target_text_number):
            self._draw_text()


    def _draw_text(self):
        font = random.choice(self.fonts)

        text = Text(font=font, text='Text!', config=self.config)
        text.set_pos(texts=self.texts)

        if isinstance(text.pos, tuple):
            self.texts.append(text)

            center = text.get_center(text.text)

            draw = ImageDraw.Draw(self.image)
            draw.text(
                (text.pos[0] - center[1], text.pos[1] - center[0]),
                text.text,
                fill = text.font_fill,
                font = text.font.get_font(text.font_size),
                stroke_width = text.stroke_width,
                stroke_fill = text.stroke_fill,
                anchor = 'lt',
                spacing = 20,
            )

            draw.line([(128, 0), (128, 256)], fill=0, width=2)
            draw.line([(0, 128), (256, 128)], fill=0, width=2)

            #self._draw_mask(text)

        
    
    def _draw_mask(self, text: Text):
        mask, offset = text.get_mask(text.text)
        height, width = mask.shape

        im_width, im_height = self.config.size

        pos = text.pos

        mask = mask[np.abs(np.clip((pos[1] - floor(height / 2)), None, 0)):np.abs(pos[1] - im_height - ceil(height / 2))]
        mask = mask[:, np.abs(np.clip(pos[0] - floor(width / 2), None, 0)):np.abs(pos[0] - im_width - ceil(width / 2))]

        new_height, new_width = mask.shape

        top_pad = np.clip(pos[1] - ceil(round(new_height / (2 / (height / new_height)), 1)), 0, im_height)
        bottom_pad = im_height - (top_pad + new_height)

        left_pad = np.clip(pos[0] - ceil(round(new_width / (2 / (width / new_width)), 1)), 0, im_width)
        right_pad = im_width - (left_pad + new_width)

        padded_mask = np.pad(mask, ((top_pad, bottom_pad), (left_pad, right_pad)))

        padded_mask = np.dstack((padded_mask, padded_mask, padded_mask))

        im1 = np.array(self.image)
        im2 = np.full((256, 256, 3), fill_value=128, dtype=np.uint8)

        self.image = np.where(padded_mask == 255, im2, im1)

        self.image = Image.fromarray(self.image)



