




import numpy as np
import cv2

from sodgen.config import Config


def rescale(im: np.ndarray, size: tuple, config: Config=Config):
    assert isinstance(im, np.ndarray), 'image needs to be numpy.ndarray'
    assert isinstance(size, tuple), 'size needs to be a tuple eg. (width, height)'

    if size[0] * size[1] > im.shape[0] * im.shape[1]:
        #upscale
        im = cv2.resize(im, size, interpolation=cv2.INTER_CUBIC)
    elif size[0] * size[1] < im.shape[0] * im.shape[1]:
        #downscale
        im = cv2.resize(im, size, interpolation=cv2.INTER_AREA)
    
    return np.array(im)