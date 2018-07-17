#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from ..config import Configuration
from ..util.color import Color

import unicodedata, re
from pprint import pprint

class Tools:

    def __init__(self):
        pass


    @staticmethod
    def verbose(verbose_level, text):
        if Configuration.verbose >= verbose_level:
            print(text)

    @staticmethod
    def ColorV(verbose_level, text):
        if Configuration.verbose >= verbose_level:
            Color.pl(text)

    @staticmethod
    def generatePattern(size=20000):
        string = ''
        for i in range(ord('A'), ord('Z') + 1):
            for j in range(ord('a'), ord('z') + 1):
                for k in range(10):
                    string += chr(i) + chr(j) + str(k)
                    if len(string) >= size:
                        return string;

        return string

    @staticmethod
    def toHex(s):
        lst = []
        for ch in s:
            hv = hex(ord(ch)).replace('0x', '')
            if len(hv) == 1:
                hv = '0' + hv
            lst.append(hv)

        return reduce(lambda x, y: x + y, lst)

    @staticmethod
    def toHex2(s):
        lst = []
        for ch in s:
            hv = hex(ord(ch)).replace('0x', '\\x')
            if len(hv) == 3:
                hv = hv.replace('\\x', '\\x0')
            lst.append(hv)

        return reduce(lambda x, y: x + y, lst)

    @staticmethod
    def toHex3(val, nbits=32):
        if nbits == 64:
            return "%16x" % ((val + (1 << nbits)) % (1 << nbits))
        else:
            return "%08x" % ((val + (1 << nbits)) % (1 << nbits))

    @staticmethod
    def toHexExport(s):
        lst = []
        for ch in s:
            hv = hex(ord(ch)).replace('0x', '\\x')
            if len(hv) == 3:
                hv = hv.replace('\\x', '\\x0')
            lst.append(hv)

        text = 'buf =  ""'
        ttext = ''
        count = 0;

        for x in lst:
            count+=1
            if (count > 16 and ttext != ''):
                text += 'buf =  "' + ttext + '"\r\n'
                ttext = ''
                count = 0
            ttext += ch

        if ttext != '':
            text += 'buf =  "' + ttext + '"\r\n'

        return text

    @staticmethod
    def toASCII(data):
        data = unicodedata.normalize('NFKD', data).encode('ascii', 'ignore')
        return data

    @staticmethod
    def addrtohex(addr, arch=32):
        if arch == 64:
            return "%16x" % addr
        else:
            return "%08x" % addr


    @staticmethod
    def getopcode(function, register, value=0, nbits=32):
        opcode = ''

        if function.lower() == "add":
            opcode += '\x81'

            if register.lower() == "eax":
                opcode += '\x00'
            elif register.lower() == "ecx":
                opcode += '\xc1'
            elif register.lower() == "edx":
                opcode += '\xc2'
            elif register.lower() == "ebx":
                opcode += '\xc3'
            elif register.lower() == "esp":
                opcode += '\xc4'
            elif register.lower() == "ebp":
                opcode += '\xc5'
            elif register.lower() == "esi":
                opcode += '\xc6'
            elif register.lower() == "edi":
                opcode += '\xc7'

            return ("%s%s" % (Tools.toHex(opcode), Tools.reversehex(Tools.toHex3(value, nbits)))).decode("hex")

        if function.lower() == "jmp":
            opcode += '\xff'

            if register.lower() == "eax":
                opcode += '\xe0'
            elif register.lower() == "ecx":
                opcode += '\xe1'
            elif register.lower() == "edx":
                opcode += '\xe2'
            elif register.lower() == "ebx":
                opcode += '\xe3'
            elif register.lower() == "esp":
                opcode += '\xe4'
            elif register.lower() == "ebp":
                opcode += '\xe5'
            elif register.lower() == "esi":
                opcode += '\xe6'
            elif register.lower() == "edi":
                opcode += '\xe7'

            return opcode

    @staticmethod
    def reversehex(hex):
        try:
            data = unicodedata.normalize('NFKD', hex).encode('ascii', 'ignore')
        except:
            data = "%s" % hex

        data = "".join(map(str.__add__, data[-2::-2], data[-1::-2]))
        return data

    @staticmethod
    def getNonCommonChars(str1):

        tmp = []
        badchars = Tools.badchars()

        for ch in badchars:
            if ch not in str1:
                if ch not in tmp:
                    tmp.append(ch)

        return tmp


    @staticmethod
    def hasNull(str1):

        for ch in str1:
            if ch == '\x00':
                return True

        return False

    '''
    @staticmethod
    def commonString(string1, string2):
        answer = ""
        len1, len2 = len(string1), len(string2)
        for i in range(len1):
            match = ""
            for j in range(len2):
                if (i + j < len1 and string1[i + j] == string2[j]):
                    match += string2[j]
                else:
                    if (len(match) > len(answer)): answer = match
                    match = ""
        return answer'''

    @staticmethod
    def longest_common_substring(s1, s2):
        try:
            m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
            longest, x_longest = 0, 0
            for x in xrange(1, 1 + len(s1)):
                for y in xrange(1, 1 + len(s2)):
                    if s1[x - 1] == s2[y - 1]:
                        m[x][y] = m[x - 1][y - 1] + 1
                        if m[x][y] > longest:
                            longest = m[x][y]
                            x_longest = x
                    else:
                        m[x][y] = 0
            return s1[x_longest - longest: x_longest]
        except:
            return ''

    @staticmethod
    def splitStrings(string):
        return [(m.group(0), m.start(), m.end() - 1) for m in re.finditer(r'\S+', string)]

    @staticmethod
    def badchars():
        '''00 colocado como ultimo caractere para caso trunque a string podemos verificar os outros caracteres'''
        return ("\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
"\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\x40"
"\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f"
"\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f"
"\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f"
"\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf"
"\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf"
"\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff\x00")