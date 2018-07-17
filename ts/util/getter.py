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
    not_found = 404

    def __init__(self, words_list, check_himself = True):
        self.words = words_list
        self.check_himself = check_himself
        requests.packages.urllib3.disable_warnings()
        pass

    def run(self, base_url):
        Getter.path_found = []
        self.base_url = base_url
        if  self.base_url.endswith('/'):
            self.base_url = self.base_url [:-1]

        self.not_found = Getter.calc_not_fount(self.base_url)

        if Configuration.verbose > 0:
            Logger.pl('{*} {W}Calculated default not found http code to this folder is {O}%d{W}' % self.not_found)

        for i in range(Configuration.tasks):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()

        for item in self.words:
            self.q.put(QueueItem("%s" % self.base_url, "%s/%s" % (self.base_url, item), self.not_found))

        self.q.join()  # block until all tasks are done
        sys.stdout.write("\033[K")  # Clear to the end of line

        return Getter.path_found

    @staticmethod
    def calc_not_fount(url):

        try:

            if url.endswith('/'):
                url = url[:-1]

            r1 = requests.get("%s/HrandfileJR" % (url), verify=False, timeout=30)

            r2 = requests.get("%s/HJR%s" % (url, Tools.random_generator(10)), verify=False, timeout=30)

            if r1.status_code == r2.status_code:
                return r1.status_code
            else:
                return 404

        except Exception as e:

            if Configuration.verbose > 0:
                Logger.pl('{*} {O}Error calculating default not found code to the folder %s: %s{W}' % (url, e))

            return 404



    def worker(self):
        try:
            while True:
                item = self.q.get()
                self.do_work(item)
                self.q.task_done()
        except KeyboardInterrupt:
            pass

    def do_work(self, queue_item):
        if not self.check_himself and queue_item.url == queue_item.base_url:
            pass
        else:
            self.get_uri("%s/" % (queue_item.url), queue_item)
        for ex in Configuration.extensions:
            self.get_uri("%s%s" % (queue_item.url, ex), queue_item, False)

    def get_uri(self, url, queue_item, check_dir=True):

        if not Configuration.full_log:
            sys.stdout.write("\033[K")  # Clear to the end of line
            print(("Testing: %s" % url), end='\r', flush=True)

        try_cnt = 0
        while try_cnt < 3:
            try:

                r = requests.get(url, verify=False, timeout=30, allow_redirects=False)
                if Configuration.full_log:
                    self.raise_url(url, r.status_code, len(r.text))
                else:
                    self.chech_if_rise(url, r.status_code, len(r.text), queue_item.not_found, check_dir)

                if Configuration.forward_location and (r.status_code == 302 or r.status_code == 301):
                    location = ''
                    try:
                        location = r.headers['Location']

                        if Configuration.verbose > 0:
                            Logger.pl('{*} {O}Forwarding to location %s from url %s{W}' % (location, url))

                        self.get_uri(location, QueueItem(queue_item.base_url,location,queue_item.not_found), check_dir)

                    except Exception as ef:

                        if Configuration.verbose > 0:
                            Logger.pl('{*} {O}Error forwarding to location %s from url %s: %s{W}' % (location, url, ef))
                        pass

                try_cnt = 4
            except Exception as e:

                if Configuration.verbose > 0:
                    Logger.pl('{*} {O}Error loading %s: %s{W}' % (url, e))
                else:
                    Logger.pl('{*} {O}Error loading %s{W}' % url)
                pass

            try_cnt + try_cnt+1

    def chech_if_rise(self, url, status_code, size, internal_not_found, check_dir=True):
        if (status_code == internal_not_found) and status_code != 404:

            '''Double check'''
            r2 = requests.get(url + '_', verify=False, timeout=30, allow_redirects=False)
            if status_code != r2.status_code:
                self.raise_url(url, r2.status_code, size)
                return

            '''else:
                if url.endswith('/') and check_dir:
                    r2 = requests.get(url[:-1], verify=False, timeout=30)
                    if r.status_code != r2.status_code:
                        self.raise_url(url, r2.status_code, len(r2.text))
                    elif  len(r2.text) - 50 <= len(r.text) <= len(r2.text) + 50:
                        self.raise_url(url, r2.status_code, len(r2.text))'''

        if status_code != internal_not_found:
            #if url.endswith('/') and check_dir:
            #    tmp_nf = Getter.calc_not_fount(url)
            #    self.chech_if_rise(url, status_code, size, tmp_nf, False)
            #else:
            self.raise_url(url, status_code, size)

    def raise_url(self, url, status, len):

        if url.endswith('/'):
            '''if status == 403:'''
            Logger.pl('==> DIRECTORY: %s (CODE:%d|SIZE:%d)' % (
            url, status, len))
            Getter.path_found.append(url)
            '''else:
            Logger.pl('==> DIRECTORY: %s ' % url)
            Getter.path_found.append(url)'''
        else:
            Logger.pl('+ %s (CODE:%d|SIZE:%d) ' % (
                url, status, len))


class QueueItem:

    url = ''
    base_url = ''
    not_found = 404

    def __init__(self, base_url, url, not_found):
        self.base_url = base_url
        self.url = url
        self.not_found = not_found
