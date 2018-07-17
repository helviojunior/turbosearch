#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from ..util.tools import Tools

import os, subprocess, socket, re, requests, queue, threading, sys

from ..config import Configuration
from ..util.logger import Logger

class Getter:

    words = []
    q = queue.Queue()
    base_url = ''
    path_found = []
    check_himself = False

    def __init__(self, words_list, check_himself = True):
        self.words = words_list
        self.check_himself = check_himself
        requests.packages.urllib3.disable_warnings()
        pass

    def run(self, base_url):
        self.path_found = []
        self.base_url = base_url
        if  self.base_url.endswith('/'):
            self.base_url = self.base_url [:-1]
        for i in range(Configuration.tasks):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()

        for item in self.words:
            self.q.put("%s/%s" % (self.base_url, item))

        self.q.join()  # block until all tasks are done
        sys.stdout.write("\033[K")  # Clear to the end of line

        return self.path_found


    def worker(self):
        try:
            while True:
                item = self.q.get()
                self.do_work(item)
                self.q.task_done()
        except KeyboardInterrupt:
            pass

    def do_work(self, item):
        if not self.check_himself and item == self.base_url:
            pass
        else:
            self.get_uri("%s/" % (item))
        for ex in Configuration.extensions:
            self.get_uri("%s%s" % (item, ex))

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
                    self.path_found.append(url)
                else:
                    Logger.pl('+ %s (CODE:%d|SIZE:%d) ' % (
                        url, r.status_code, len(r.text)))


        except Exception as e:
            Logger.pl('! Error loading %s ' % url)
            pass
