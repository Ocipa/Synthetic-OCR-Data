


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
            (128 - center[1], 128 - center[0]),
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

        #self._draw_mask(text)

        
    
    def _draw_mask(self, text: Text):
        mask, offset = text.get_mask('00')
        height, width = mask.shape

        center = text.get_center('00')

        # b_pad = 128 - int(height / 2)
        # t_pad = 256 - (b_pad + height)

        # r_pad = 128 - int(width / 2)
        # l_pad = 256 - (r_pad + width)

        t_pad = 128 - int(height / 2) + int(offset[1])
        b_pad = 256 - (t_pad + height)

        l_pad = 128 - int(width / 2) + int(offset[0])
        r_pad = 256 - (l_pad + width)

        mask = np.pad(mask, ((t_pad, b_pad), (l_pad, r_pad)))
        mask = np.dstack((mask, mask, mask))

        im1 = np.array(self.image)
        im2 = np.full((256, 256, 3), fill_value=128, dtype=np.uint8)

        #self.image = mask / 255 * im2 + (1 - mask / 255) * im1

        self.image = np.where(mask == 255, im2, im1)



