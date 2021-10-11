



import random
from decimal import Decimal
import numpy as np
from PIL import Image, ImageDraw

from math import radians, cos, sin, inf
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


def rotate_point(p, center, angle):
    '''
    rotate a point around center by a angle
    '''
    x, y = (p[0] - center[0], p[1] - center[1])

    r = radians(angle)

    x1 = round(x * cos(r) - y * sin(r)) + center[0]
    y1 = round(y * cos(r) + x * sin(r)) + center[1]

    return (x1, y1)

def rotate_bbox(bbox: list, center: tuple=(0, 0), angle: int=0):
    '''
    rotate a bbox around center by a angle

    ---
    :param bbox: a list of corners eg. [(c1), (c2), (c3), (c4)]
    :param center: a point eg. (x, y)
    :param angle: a integer to rotate points by eg. 45

    ---
    ->return: a list of corners eg. [(c1), (c2), (c3), (c4)] rotated by angle
    '''
    new_bbox = []

    for i in bbox:
        if isinstance(i, list):
            new_bbox.append(rotate_bbox(i, center=center, angle=angle))
        
        else:
            x, y = i
            x1, y1 = rotate_point((x, y), center, -angle)

            new_bbox.append((x1, y1))

    return new_bbox


def translate_bbox(bbox: list, offset: tuple=(0, 0)):
    '''
    translates a bbox by offset

    ---
    :param bbox: a list of corners eg. [(c1), (c2), (c3), (c4)]
    :param offset: a tuple to translate each point by eg. (x, y)

    ---
    ->return: a list of corners eg. [(c1), (c2), (c3), (c4)] translated by offset
    '''
    new_bbox = []

    for i in bbox:
        if isinstance(i, list):
            new_bbox.append(translate_bbox(i, offset))
        
        else:
            x, y = i
            x1, y1 = (x + offset[0], y + offset[1])

            new_bbox.append((x1, y1))

    return new_bbox

def extrema_from_points(points: list):
    '''
    gets the minx, miny, maxx, maxy from a list of points

    ---
    :param points: a list of points eg. [(x1, y1), (x2, y2)]

    ---
    ->return: a list with 2 points [(minx, miny), (maxx, maxy)] from a list of points
    '''
    minx, miny = (inf, inf)
    maxx, maxy = (-inf, -inf)

    for i in points:
        if isinstance(i, list):
            (minx2, miny2), (maxx2, maxy2) = extrema_from_points(i)

            minx, miny = (min(minx, minx2), min(miny, miny2))
            maxx, maxy = (max(maxx, maxx2), max(maxy, maxy2))

        else:
            x, y = i

            minx, miny = (min(minx, x), min(miny, y))
            maxx, maxy = (max(maxx, x), max(maxy, y))
    
    return [(minx, miny), (maxx, maxy)]


def config_value_to_value(value: ...) -> ...:
    '''
    takes a variety of types of values and returns the respective value for that type

    ---
    :param value:
        - list: picks random value from the list, with random.choice
        - tuple:
            * (int x, int y): picks a random value between x and y with random. randint
            * (float x, float y, optional int z): picks a random value between x and y
            with random.uniform and rounds to z values after the decimal, be default, z is
            the value of numbers after the decimal in x
        - int: returns value unchanged
        - string: returns value unchanged
        - function: returns value unchanged
        - other: returns value unchanged
    
    ---
    ->return: a value, respectively to the input value
    '''
    if isinstance(value, (list, np.ndarray)):
        val = random.choice(value)

        return val
    elif isinstance(value, tuple):
        x, y, z, *_ = (*value, None)

        if isinstance(x, int):
            y = int(y)
            val = random.randint(x, y)

            return val
        elif isinstance(x, float):
            y = float(y)
            if z == None:
                z = len(str(Decimal(str(x)) % 1)) - 2

            val = round(random.uniform(x, y), z)
            
            return val

    return value