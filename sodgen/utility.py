



import numpy as np
from PIL import Image, ImageDraw

from time import time


def get_im_mode(im):
    '''
    returns image mode RGB or RGBA
    '''
    if not isinstance(im, np.ndarray):
        im = np.array(im)
    
    height, width, ch = im.shape

    mode = 'RGB' if ch == 3 else 'RGBA'

    return mode

def rgba2rgb(im):
    if not isinstance(im, np.ndarray):
        im = np.array(im)
    
    height, width, ch = im.shape

    if ch == 3:
        return im

    assert ch == 4, f'RGBA image has 4 channels, {type(im)} has {ch} channels'

    r, g, b, a = np.dsplit(im, 4)
    rgb_im = np.dstack((r, g, b))

    return rgb_im

def rgb2rgba(im):
    if not isinstance(im, np.ndarray):
        im = np.array(im)
    
    height, width, ch = im.shape

    if ch == 4:
        return im

    assert ch == 3, f'RGB image has 3 channels, {type(im)} has {ch} channels'

    r, g, b = np.dsplit(im, 3)
    a = np.full(r.shape, fill_value=255)

    rgba_im = np.dstack((r, g, b, a))

    return rgba_im



def render_bounding_box(
        image: np.ndarray,
        corners: list,
        outline_color: tuple=(40, 225, 40),
        width: int=2,
        fill: int=60
    ):
    '''
    renders a bounding box around a list of corners

    ---
    :param image: the image the bounding box will be rendered onto,
        image must be numpy.ndarray or convertible with numpy.array()
    :param corners: a list of corners eg. [(c1), (c2), (c3), (c4)]
    :param outline_color: RGB tuple for the color of the outline of
        the bounding box
    :param width: the width of the outline in pixels
    :param fill: the alpha value of the fill, eg. 0 will have no fill
        and 255 will be opaque
    
    ---
    ->return: a numpy.ndarray image
    '''
    if not isinstance(image, np.ndarray):
        image = np.array(image)

    if get_im_mode(image) == 'RGBA':
        image = rgba2rgb(image)
        
    image = Image.fromarray(image)
    draw = ImageDraw.Draw(image, mode='RGBA')

    draw.line([*corners, corners[0], corners[1]], fill=outline_color, width=width, joint='curve')
    draw.polygon([*corners], fill=(*outline_color, fill))

    return np.array(image)


def rotate_bbox(angle: int=0):
    pass