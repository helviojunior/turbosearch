#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from ..util.tools import Tools

import os, subprocess, socket, re, queue, threading, sys

from ..config import Configuration
from ..util.logger import Logger
from ..util.getter import Getter

class PathGetter:

    words = []
    q = queue.Queue()
    added = []

    def __init__(self):
        pass

    def load_wordlist(self):
        with open(Configuration.word_list, 'r', encoding="ascii", errors="surrogateescape") as f:
            line = f.readline()
            while line:
                if line.endswith('\n'):
                    line = line[:-1]
                if line.endswith('\r'):
                    line = line[:-1]

                line = ''.join(filter(self.permited_char, line))
                self.words.append(line.strip())

                try:
                    line = f.readline()
                except:
                    pass

    def len(self):
        return len(self.words)

    def permited_char(self, s):
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

    def run(self):


        t = threading.Thread(target=self.worker)
        t.daemon = True
        t.start()

        self.added.append(Configuration.target)
        self.q.put(Configuration.target)

        self.q.join()  # block until all tasks are done
        sys.stdout.write("\033[K")  # Clear to the end of line


    def worker(self):
        try:
            while True:
                item = self.q.get()

                if item != Configuration.target:
                    Logger.pl('  ')
                    Logger.pl('{+} {W}Entering directory: {C}%s{W} ' % item)

                get = Getter(self.words, False)
                paths_found = get.run(item)

                if Configuration.verbose > 0:
                    Logger.pl('{*} {W}We got {O}%d{W} new directories to check from url %s{W}' % (len(paths_found), item))

                for u in paths_found:
                    if u.endswith('/'):
                        u = u[:-1]
                    if u not in self.added:
                        self.added.append(u)
                        self.q.put(u)

                self.q.task_done()
        except KeyboardInterrupt:
            pass
