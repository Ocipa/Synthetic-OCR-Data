


from sodgen.config import Config
from sodgen.fonts import *
from sodgen.image import *

import os


class generator:
    def __init__(self, config: Config=Config):
        self.config = config

        self.fonts = self._get_fonts()


    def _get_fonts(self):
        fonts_dir = None
        fonts = []

        if not self.config.fonts_dir or not isinstance(self.config.fonts_dir, str):
            assert self.config.auto_download_fonts, 'missing fonts directory and auto download fonts is False in the config'

            fonts_dir = './fonts_dir'
        else:
            fonts_dir = self.config.fonts_dir
        
        if not os.path.isdir(fonts_dir):
            download_fonts_dir(path=fonts_dir)
        
        assert os.path.isdir(fonts_dir), 'invalid fonts_dir'

        assert self.config.lang, f'{self.config.lang} is a invalid language code'
        fonts = get_fonts_from_dir(path=fonts_dir, lang=self.config.lang)
    
        return fonts
    

    def generate_images(self, num: int=1):
        images = []

        for i in range(1, num + 1):
            im = image(self.fonts, config=self.config)

            if im:
                images.append(im)
        
        return images
        


