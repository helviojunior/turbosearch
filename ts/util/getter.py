#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from ..util.tools import Tools

import os, subprocess, socket, re, requests, queue, threading, sys

from ..config import Configuration
from ..util.logger import Logger

class Getter:

    words = []
    q = queue.Queue()

    def __init__(self):
        requests.packages.urllib3.disable_warnings()
        pass

    def load_wordlist(self):
        with open(Configuration.word_list, 'r') as f:
            line = f.readline()
            while line:
                if line.endswith('\n'):
                    line = line[:-1]
                if line.endswith('\r'):
                    line = line[:-1]
                self.words.append(line)
                try:
                    line = f.readline()
                except:
                    pass

    def len(self):
        return len(self.words)


    def run(self):
        Logger.pl('{+} {W}Scanning url {C}%s{W} ' % Configuration.target)

        for i in range(Configuration.tasks):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()

        for item in self.words:
            self.q.put(item)

        self.q.join()  # block until all tasks are done
        sys.stdout.write("\033[K")  # Clear to the end of line


    def worker(self):
        try:
            while True:
                item = self.q.get()
                self.do_work(item)
                self.q.task_done()
        except KeyboardInterrupt:
            pass

    def do_work(self, item):
        self.get_uri("%s/%s" % (Configuration.target, item))
        for ex in Configuration.extensions:
            self.get_uri("%s/%s%s" % (Configuration.target, item, ex))

    def get_uri(self, url):
        sys.stdout.write("\033[K")  # Clear to the end of line
        print(("%s" % url), end='\r', flush=True)

        try:

            requests.packages.urllib3.disable_warnings()
            r = requests.get(url, verify=False, timeout=30)

            '''
            ==> DIRECTORY: http://10.11.1.219/html5/                                                                
            + http://10.11.1.219/index.html (CODE:200|SIZE:11510)                                                   
            + http://10.11.1.219/server-status (CODE:403|SIZE:215) 
            '''

            if (r.status_code >= 200 and r.status_code < 400) or (r.status_code >= 500 and r.status_code <= 599):

                if url.endswith('/'):
                    Logger.pl('==> DIRECTORY: %s ' % url)
                else:
                    Logger.pl('+ %s (CODE:%d|SIZE:%d) ' % (
                        url, r.status_code, len(r.text)))


        except Exception as e:
            Logger.pl('! Error loading %s ' % url)
            pass
