


from sodgen.config import Config
from sodgen.fonts import *
from sodgen.image import *
from sodgen.corpus import Corpus
from sodgen.utility import config_value_to_value

import os


class generator:
    def __init__(self, config: Config=Config):
        self.config = config

        self.fonts = self._get_fonts()
        self.corpus = self._get_corpus()

        self.images = []

        self.dataset = self.config.dataset_class(config=self.config)


    def _get_fonts(self):
        fonts_dir = None
        fonts = []

        fonts_dir = config_value_to_value(self.config.fonts_dir)
        assert os.path.isdir(fonts_dir), f'{fonts_dir} is not a valid directory'

        assert self.config.lang, f'{self.config.lang} is a invalid language code'
        fonts = get_fonts_from_dir(path=fonts_dir, lang=self.config.lang)
    
        return fonts
    
    def _get_corpus(self):
        corpus = None
        if self.config.corpus_path and isinstance(self.config.corpus_path, str):
            assert os.path.isfile(self.config.corpus_path), 'corpus_path needs to lead to a file'

            corpus = Corpus(self.config.corpus_path)
        else:
            corpus = Corpus()
        
        return corpus
    

    def generate_images(self, num: int=1):
        for i in range(1, num + 1):
            im = image(self.fonts, corpus=self.corpus, config=self.config)

            if im:
                self.images.append(im)
        
        #self.dataset.add_image(images[0])
        
        return self.images

    def export_images(self):
        for i in self.images:
            self.dataset.add_image(i)
        
        self.dataset.export()
        


