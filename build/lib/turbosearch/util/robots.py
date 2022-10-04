#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys, os.path, re
import string, base64
from urllib.parse import urlparse

from .getter import Getter
from .color import Color
from .logger import Logger
from .tools import Tools
from ..config import Configuration

class Robots(object):
    base_path = ''
    robots_txt = ''
    word_list = []
    uri_list = []

    def __init__(self, base_path):
        self.base_path = base_path

        if Configuration.norobots:
            return

        if Configuration.case_insensitive:
            self.base_path = base_path.lower()

        rUri = urlparse(self.base_path)

        try:
            Logger.pl('{+} {W}Getting informations from /robots.txt at {C}%s{W} ' % rUri.netloc)

            proxy1={}

            if Configuration.proxy != '':
                proxy1 = {
                  'http': Configuration.proxy,
                  'https': Configuration.proxy,
                }

            url1 = "%s://%s/robots.txt" % (rUri.scheme, rUri.netloc)
            r1 = Getter.general_request(url1, proxy1, "GET")
            if r1 is not None and r1.status_code == 200 and len(r1.text) > 0:
                self.robots_txt += str(r1.text)

                if Configuration.proxy_report_to != '':
                    try:
                        proxy={}

                        proxy = {
                          'http': Configuration.proxy_report_to,
                          'https': Configuration.proxy_report_to,
                        }
                        
                        Getter.general_request(url1, proxy, "GET")

                    except Exception as e:
                        print(e)
                        pass

                try:
                    if Configuration.db is not None:
                        Configuration.db.insertUri(url1, r1.status_code, len(r1.text))
                except:
                    pass

            url2 = "%s://%s%s/robots.txt" % (rUri.scheme, rUri.netloc, "/" + rUri.path.strip("/"))
            url2 = url2.replace("//robots.txt", "/robots.txt")
            if url1 != url2:
                r1 = Getter.general_request(url2, proxy1, "GET")
                if r1 is not None and r1.status_code == 200 and len(r1.text) > 0:
                    self.robots_txt += str(r1.text)
                    
                    if Configuration.proxy_report_to != '':
                        try:
                            proxy={}

                            proxy = {
                              'http': Configuration.proxy_report_to,
                              'https': Configuration.proxy_report_to,
                            }
                            
                            Getter.general_request(url2, proxy, "GET")

                        except Exception as e:
                            pass

                    try:
                        if Configuration.db is not None:
                            Configuration.db.insertUri(url2, r1.status_code, len(r1.text))
                    except:
                        pass

            self.parse()
        except Exception as e:
            print(e)
            pass

    def parse(self):
        paths = []
        lines = self.robots_txt.replace("\r", "\n").split("\n")
        rUri = urlparse(self.base_path)
        for line in lines:
            if line.endswith('\n'):
                line = line[:-1]

            if Configuration.case_insensitive:
                line = line.lower()

            if 'disallow:' in line.lower() or 'allow:' in line.lower():
                m = re.search("(?P<url>/[^\s]+)", line)
                if m is not None:
                    path = m.group("url")
                    path = ''.join(filter(Tools.permited_char, path)).strip()
                    if path not in paths:
                        paths.append(path.strip("/"))

        for path in paths:
            vp = "%s://%s/%s" % (rUri.scheme, rUri.netloc, path) 
            if self.base_path in vp:
                if path not in self.uri_list:
                    self.uri_list.append(path)
            
            parts = path.split("/")
            for p in parts:
                if p not in self.word_list and p not in self.uri_list:
                    self.word_list.append(p)

        if len(self.word_list) > 0 or len(self.uri_list) > 0:
            Logger.pl('{+} {W}Loaded {O}%s{W} path(es) and {O}%s{W} unique word(s) from /robots.txt' % (len(self.uri_list), len(self.word_list)))
            for p in self.uri_list:
                Logger.pl('==> ENTRY: /%s' % (p))
        
        Logger.pl(" ")

    def getWordList(self):
        return self.word_list

    def getUriList(self):
        return self.uri_list
