

import os
import random
import string
import textwrap
import csv

from sodgen.config import Config



class Corpus:
    def __init__(self, path: str=None):
        self.name = 'Unnamed'

        if path:
            assert path, 'attempted to create corpus without path to corpus'
            assert os.path.isfile(path), 'corpus path does not lead to file'

            name, extension = os.path.splitext(path)
            assert extension == '.csv', 'corpus only supports .csv'

            self.name = name
        self.path = path

        if self.path:
            self._corpus_to_lines()
    
    def _corpus_to_lines(self):
        lines = []

        with open(self.path, newline='') as f:
            reader = csv.reader(filter(lambda row: row[0]!='#', f))
            for row in reader:
                if len(row) > 0: 
                    lines.append(str(row[0]))

        self.lines = lines
    
    def _random_str(self, length: int=(4, 12), chars: str=string.ascii_letters):
        if isinstance(length, tuple):
            length = random.randrange(*length)
    
        return ''.join([random.choice(chars) for i in range(length)])
    
    def get_random_line(self, config: Config=Config):
        s = None

        if self.path:
            s = random.choice(self.lines)
        else:
            s = self._random_str()

        if config.max_characters:
            s = s[:config.max_characters]

        if config.max_line_length:
            s = textwrap.wrap(s, width=config.max_line_length)
        
        if config.text_multiline and isinstance(s, list):
            s = '\n'.join(s)
        elif isinstance(s, list):
            s = s[0]
        
        return s