#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import string, random, sys, re

class Tools:

    def __init__(self):
        pass

    @staticmethod
    def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))


    @staticmethod
    def clear_line():
        sys.stdout.write("\033[K")  # Clear to the end of line


    @staticmethod
    def check_content(result):
        try:
            if result is not None and len(Configuration.text_to_find) > 0:
                data = '\r\n' + result.request.url + '\r\n'
                data += '\r\n'.join('{}: {}'.format(k, v) for k, v in result.headers.items())
                data += '\r\n\r\n'
                data += result.text
                data = data.replace('\n','\n      ')
                for f in Configuration.text_to_find:
                    indexes = [m.start() for m in re.finditer(f, data)]
                    if len(indexes) > 0:
                        for i in indexes:
                            Logger.pl('* %s (TEXT:%s|POSITION:%d) ' % (result.request.url, f, i))
                        Logger.pl_file('--> Start Response: ')
                        Logger.pl_file(data)
                        Logger.pl_file('<-- End Response')
        except:
            pass


    @staticmethod     
    def permited_char(s):
        if s.isalpha():
            return True
        elif bool(re.match("^[A-Za-z0-9_-]*$", s)):
            return True
        elif s == ".":
            return True
        elif s == "/":
            return True
        else:
            return False