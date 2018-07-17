#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import string, random, sys

class Tools:

    def __init__(self):
        pass

    @staticmethod
    def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))


    @staticmethod
    def clear_line():
        sys.stdout.write("\033[K")  # Clear to the end of line

