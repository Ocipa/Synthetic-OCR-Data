


from sodgen.config import Config
from sodgen.fonts import *
from sodgen.image import *

import os



def generate(num: int=1, config=Config) -> str:
    '''
    test
    
    ---
    num: amount of images to generate
    config: the configuration to create the data
    
    ---
    -> return: a path to output_dir
    '''
    assert config.output_dir, 'missing output_dir, change in config'

    images = []
    fonts = []

    if not config.fonts_dir:
        assert config.auto_download_fonts, 'missing fonts directory and auto download fonts is False in the config'

        download_fonts_dir(path='./fonts_dir')
        fonts_dir = './fonts_dir'
    else:
        fonts_dir = config.fonts_dir
    
    assert os.path.isdir(fonts_dir), 'invalid fonts_dir'

    assert config.lang, f'{config.lang} is a invalid language code'
    fonts = get_fonts_from_dir(path=fonts_dir, lang=config.lang)


    for i in range(1, num + 1):
        im = image(fonts, config=config)

        if im:
            images.append(im)










    #print(f'for {config.lang}, {len(fonts)} were found')

    return images