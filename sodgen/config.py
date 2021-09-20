import sodgen.color as color


class Config:
    def __init__(self):
        pass

    #
    lang = None

    #
    corpus_path = None

    #
    output_dir = '../output/' #to-do

    ####################
    #### FONT STUFF ####
    ####################

    #
    auto_download_fonts = True
    fonts_dir = None

    #(min, max)
    font_size = (30, 100)

    #(min, max)
    stroke_width = (2, 6)

    #Color to fill for the text, int, rgb tuple or None for random
    font_fill = None

    #
    stroke_fill = color.complementary

    #int or tuple
    target_text_number = 1

    #
    text_multiline = False #to-do

    #
    text_overlap = False

    #
    text_force_inbounds = True

    #####################
    #### IMAGE STUFF ####
    #####################

    #(width, height)
    size = (256, 256)

    #
    backgrounds_dir = None #to-do

