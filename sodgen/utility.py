



import numpy as np
import skia # type: ignore
from math import radians, cos, sin, inf
import random
from decimal import Decimal


def render_bounding_box(
        canvas,
        bbox: list,
        color: tuple=(40, 225, 40),
        stroke_width: int=2,
        fill_alpha: int=60
    ) -> None:
    '''
    renders a bounding box

    ---
    :param canvas: the image the bounding box will be rendered onto,
        canvas must be skia.Canvas
    :param bbox: a bbox eg. [(c1), (c2), (c3), (c4)]
    :param color: RGB tuple for the color of the bounding box
    :param stroke_width: the width of the outline stroke in pixels
    :param fill_alpha: the alpha value of the fill, eg. 0 will have no fill
        and 255 will be opaque
    
    ---
    ->return: None
    '''
    assert isinstance(canvas, skia.Canvas), "render_bounding_box: canvas needs to be a skia.Canvas"

    paint = skia.Paint(
        AntiAlias = True,
        Color = skia.ColorSetARGB(fill_alpha, *color[::-1]),
        Style = skia.Paint.kStrokeAndFill_Style,
        StrokeWidth = stroke_width
    )

    path = skia.Path()
    path.moveTo(*bbox[0])
    for i in [*bbox[::-1]]:
        path.lineTo(*i)
    path.close()
    
    canvas.drawPath(path, paint)

    if stroke_width > 0:
        paint.setARGB(255, *color[::-1])
        paint.setStyle(skia.Paint.kStroke_Style)
        paint.setPathEffect(skia.DashPathEffect.Make([stroke_width * 2, stroke_width * 3], 0.0))

        canvas.drawPath(path, paint)

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


def extra_bytes(txt: str, encoding: str='utf8') -> int:
    '''
    returns the amount of "extra bytes" from a utf string,
    where the 'extra bytes' is the amount of bytes in each
    character, minus 1. (eg. "a" is 0 'extra bytes', "???"
    is 2 'extra bytes')

    ---
    :param txt: the string to get 'extra bytes' from
    :param encoding: the encoding type of txt

    ---
    ->return: number of 'extra bytes'
    '''
    num = 0

    for i in txt:
        lb = len(bytes(i, encoding))

        num += (lb - 1)
    
    return num