


from typing import Text
from sodgen import config
from sodgen.config import Config
from sodgen.fonts import *

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
        
        self.image = Image.fromarray(self.image)

        '''
        do background stuff here
        '''

        self._draw_text()


    def _draw_text(self):
        font = random.choice(self.fonts)

        text = Text(font=font, config=self.config)

        draw = ImageDraw.Draw(self.image)
        draw.text(
            (0, 0),
            'test',
            fill = text.font_fill,
            font = text.font.get_font(text.font_size),
            stroke_width = text.stroke_width,
            stroke_fill = text.stroke_fill
        )
