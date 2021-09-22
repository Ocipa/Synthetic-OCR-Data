


from sodgen.config import Config
from sodgen.preprocessing import *

import os
import numpy as np
import random


def random_background(config: Config=Config):
    dir_path = config.backgrounds_dir

    if dir_path:
        assert os.path.isdir(dir_path), "dir_path needs to be a path to a directory"

        a = random.choice(os.listdir(dir_path))

        im = cv2.cvtColor(cv2.imread(dir_path + '/' + a), cv2.COLOR_BGR2RGBA)
        im = np.array(im)

        im = rescale(im, config.size)

        return im
    
    else:
        c = (random.randint(90, 180), random.randint(90, 180), random.randint(90, 180), 255)
        im = np.full(shape=(config.size[1], config.size[0], 4), fill_value=c, dtype='uint8')

        return im

