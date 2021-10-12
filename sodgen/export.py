
import os
import shutil
import string
import json
import random

from PIL.Image import fromarray


# default annotation example
# [
# 	{
# 		"path": "./images/001.jpg",
# 		"size": (512, 512),
# 		"annotations": [
# 			{
# 				"group": 1,
# 				"text": "Hello",
# 				"bbox": [(25, 25), (75, 25), (75, 50), (25, 50)]
# 			},
# 			{
# 				"group": 1,
# 				"text": "World!",
# 				"bbox": [(25, 50), (75, 50), (75, 75), (25, 75)]
# 			},
# 			{
# 				"group": 2,
# 				"text": "Yo",
# 				"bbox": [(100, 25), (150, 25), (150, 50), (100, 50)]
# 			},
# 			{
# 				"group": 2,
# 				"text": "dude!",
# 				"bbox": [(100, 50), (150, 50), (150, 75), (100, 75)]
# 			}
# 		]
# 	},
# 	{
# 		"path": "../images/002.jpg",
# 		"size": (512, 512),
# 		"annotations": [
# 			...
# 		]
# 	}
# ]


def get_ordinal_name(path, default_name='00000000', extension='.png'):
    '''
    
    '''
    pass


def get_random_name(path, chars=string.ascii_letters, length=8, extension='.png'):
    '''
    
    '''
    l = os.listdir(path)
    name = None

    while name in l or name == None:
        name = ''.join([random.choice(chars) for i in range(length)])
    
    return name + extension



class default_dataset:
    def __init__(self, config):
        self.config = config

        self._create_export_folders()

        self.path = self.config.export_path
        self.images_path = os.path.join(self.path, 'images')
        self.annotations_path = os.path.join(self.path, 'annotations.json')

        self.json_file = None
        with open(self.annotations_path, 'r', encoding='utf8') as f:
            self.json_file = json.load(f)

    def add_image(self, image):
        name = get_random_name(self.images_path)

        # TODO: test saving with skia rather than with PIL, if as
        # fast and as good quality with both file size and image
        # quality, then replace PIL with skia
        im = fromarray(image.image)
        im.save(self.images_path + '/' + name, format='PNG')

        annotation = {
            'path': name,
            'width': im.width,
            'height': im.height,
            'annotations': []
        }

        for i, v in enumerate(image.texts):
            text = v.text.split('\n')
            for i2, v2 in enumerate(v.bbox):
                d = {
                    'group': i,
                    'text': text[i2],
                    'bbox': [
                        # NOTE: json can't serialize numpy numbers, so this ugly
                        # is converting numpy.uint8 in the bbox to python int
                        [int(v2[0][0]), int(v2[0][1])],
                        [int(v2[1][0]), int(v2[1][1])],
                        [int(v2[2][0]), int(v2[2][1])],
                        [int(v2[3][0]), int(v2[3][1])]
                    ]
                }

                annotation['annotations'].append(d)

        self.json_file.append(annotation)
    
    def export(self):
         with open(self.annotations_path, 'w', encoding='utf8') as f:
            json.dump(self.json_file, f)
        

    def _create_export_folders(self, delete_existing: bool=False):
        path = self.config.export_path

        if os.path.isdir(path):
            if delete_existing:
                shutil.rmtree(path)

                os.mkdir(path)
        
        else:
            os.mkdir(path)
        
        if not os.path.isdir(path + '/images'):
            os.mkdir(path + '/images')
        
        if not os.path.isfile(path + '/annotations.json'):
            with open(path + '/annotations.json', 'w') as f:
                f.write('[]')

