


from sodgen import config, utility
from sodgen.config import Config
from sodgen.fonts import *
from sodgen.corpus import *
from sodgen.background import *
from sodgen.utility import config_value_to_value as to_value

from math import floor, ceil
import matplotlib.pyplot as plt
import skia # type: ignore

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

        self.image = random_background(config=self.config)

        self.surface = skia.Surface(self.image)
        self.canvas = self.surface.getCanvas()

        self.target_text_number = to_value(self.config.target_text_number)

        for i in range(self.target_text_number):
            self._draw_text()

    def _draw_text(self):
        font = random.choice(self.fonts)

        random_text = self.corpus.get_random_line(config=self.config)
        text = Text(font=font, text=random_text, config=self.config)
        # TODO: find_pos needs to be called in image module
        # since it needs the other texts in the image for when
        # allow_overlap is false, maybe pass the other texts
        # when building text class, and find_pos during __init__ ??
        text.find_pos(texts=self.texts)

        if isinstance(text.pos, tuple):
            # NOTE: if unable to find position for text, text.pos
            # and text.bbox is None.
            self.texts.append(text)

            text.render_text(self.canvas)




