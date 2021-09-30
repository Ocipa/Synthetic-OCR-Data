


from sodgen import config, utility
from sodgen.config import Config
from sodgen.fonts import *
from sodgen.corpus import *
from sodgen.background import *

from math import floor, ceil

import random
import numpy as np
import cv2

import textwrap


class image():
    def __init__(self, fonts: list, corpus: Corpus, config: Config):
        assert isinstance(fonts, list), 'missing fonts, or fonts is not a list'
        assert isinstance(config, Config), 'config is not a Config object'

        self.fonts = fonts
        self.config = config
        self.corpus = corpus

        self.texts = []

        self._build()
    
    def _build(self):
        width, height = self.config.size

        #self.image = np.full((height, width, 3), fill_value=255, dtype=np.uint8)
        self.image = random_background(config=self.config)
        
        self.image = Image.fromarray(self.image, mode='RGBA')


        self.target_text_number = self.config.target_text_number
        if isinstance(self.target_text_number, tuple):
            self.target_text_number = random.randint(*self.target_text_number)
        
        for i in range(self.target_text_number):
            self._draw_text()
        
        self._combine_text()


    def _draw_text(self):
        font = random.choice(self.fonts)

        random_text = self.corpus.get_random_line(config=self.config)
        text = Text(font=font, text=random_text, config=self.config)
        text.set_pos(texts=self.texts)

        if isinstance(text.pos, tuple):
            self.texts.append(text)

            #self._draw_mask(text)
    
    def _combine_text(self):
        for i in self.texts:
            text_image = np.full((self.config.size[1], self.config.size[0], 4), 0, dtype='uint8')
            text_image = Image.fromarray(text_image, mode='RGBA')

            pos = (int(i.pos[0] + i.render_offset[0]), int(i.pos[1] + i.render_offset[1]))
            text_image.paste(Image.fromarray(i.render, mode='RGBA'), pos)

            self.image = Image.alpha_composite(self.image, text_image)
            
            # self.image = Image.fromarray(self.image, 'RGBA')
        
        # for i in self.texts:
        #     for i in i.lines_bbox:
        #         self.image = utility.render_bounding_box(
        #             self.image,
        #             i
        #         )
        
        self.image = self.image.convert('RGB')
        #self.image = Image.fromarray(self.image)
        # draw = ImageDraw.Draw(self.image)




