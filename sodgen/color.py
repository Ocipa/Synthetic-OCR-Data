

import random





def to_rgb(option=None):
    '''
    will return option if option is a rgb color tuple \n
    will return (option) * 3 if option is a int \n
    will retunr random rgb color tuple if option is None
    '''
    c = None

    if isinstance(option, tuple):
        c = option

    elif isinstance(option, int):
        c = (option, option, option)

    else:
        c = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    return c


@staticmethod
def complementary(color: tuple):
    r, g, b = color

    comp_color = (255 - r, 255 - g, 255 - b)

    return comp_color