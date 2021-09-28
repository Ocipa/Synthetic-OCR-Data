import sodgen.color as color
import sodgen.export as export


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
    font_size = (12, 16)

    #(min, max)
    stroke_width = (1, 2)

    #Color to fill for the text, int, rgb tuple or None for random
    font_fill = None

    #
    stroke_fill = color.complementary

    #string: 'left' 'center' 'right' or list of strings: ['left', 'center']
    text_align = 'left'

    #int or list of rotations eg. [0, 90, 180, 270] or numpy.arange(0, 360, 45)
    text_rotation = 0

    #int or tuple
    target_text_number = 1

    #
    text_multiline = True

    #int or tuple eg. (min, max), does nothing on single line text
    line_spacing = (2, 8)

    #
    max_line_length = 80

    #
    max_characters = None

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

    ######################
    #### EXPORT STUFF ####
    ######################

    #
    dataset_class = export.default_dataset

    #
    export_path = './dataset'

    #
    image_save_format = 'jpeg'


