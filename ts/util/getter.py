#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from ..util.tools import Tools

import os, subprocess, socket, re, requests, queue, threading, sys, operator, time, json

from ..config import Configuration
from ..util.logger import Logger

class Getter:

    '''Static variables'''
    path_found = []
    check_himself = False
    dir_not_found = 404
    not_found_lenght = -1
    checked = 0
    total = 0
    ingore_until = ''
    error_count = 0


    '''Local non-static variables'''
    q = queue.Queue()
    words = []
    base_url = ''
    last = {}
    running=True
    

    def __init__(self, words_list, check_himself = True):
        self.words = words_list
        Getter.check_himself = check_himself
        Getter.checked = 0
        Getter.total = 0
        Getter.ingore_until = ''
        Getter.dir_not_found = 404
        Getter.not_found_lenght = -1
        Getter.path_found = []

        requests.packages.urllib3.disable_warnings()
        pass

    def add_checked(self):
        if Getter.checked < Getter.total:
            Getter.checked += 1

    def stop(self):
        self.running=False

    def run(self, base_url):
        Getter.path_found = []
        Getter.base_url = base_url

        if  Getter.base_url.endswith('/'):
            Getter.base_url = Getter.base_url [:-1]

        (Getter.dir_not_found, Getter.not_found_lenght) = Getter.calc_not_fount(Getter.base_url)

        if Getter.not_found_lenght > 0:
            Logger.pl('{*} {W}Calculated default not found http code for this folder is {O}%d{W} with content size {O}%d{W}' % (Getter.dir_not_found, Getter.not_found_lenght))
        else:
            Logger.pl('{*} {W}Calculated default not found http code for this folder is {O}%d{W} with no content' % (Getter.dir_not_found))

        for i in range(Configuration.tasks):
            self.last[i] = ''
            t = threading.Thread(target=self.worker, kwargs=dict(index=i))
            t.daemon = True
            t.start()

        insert = True
        if self.ingore_until != '':
            insert = False

        Getter.total = len(self.words)
        for item in self.words:
            if self.running and item.strip() != '':
                if not insert and item == self.ingore_until:
                    insert = True
                if insert:
                    self.q.put(DirectoryInfo("%s/%s" % (Getter.base_url, item), Getter.dir_not_found))
                else:
                    self.add_checked()

        self.q.join()  # block until all tasks are done
        Tools.clear_line()

        return Getter.path_found


    @staticmethod
    def calc_not_fount(url):

        extensions_not_found = {}
        extensions_not_found["__root__"] = DirectoryInfo('', 404, -1)

        try:

            if url.endswith('/'):
                url = url[:-1]

            r1 = requests.get("%s/HrandfileJR" % (url), verify=False, timeout=30)

            r2 = requests.get("%s/HJR%s" % (url, Tools.random_generator(10)), verify=False, timeout=30)

            if r1.status_code == r2.status_code:
                extensions_not_found["__root__"] =  DirectoryInfo('', r1.status_code, len(r1.text))
            else:
                extensions_not_found["__root__"] = DirectoryInfo('', 404, -1)

        except Exception as e:
            extensions_not_found["__root__"] = DirectoryInfo('', 404, -1)

            if Configuration.verbose > 0:
                Logger.pl('{*} {O}Error calculating default not found code to the folder %s: %s{W}' % (url, e))


        if Configuration.verbose > 4:
            Logger.pl('{?} {G}Checking not found: %s {O}%s - %d{W}' % (url, "__root__", extensions_not_found["__root__"]))


        for ex in Configuration.extensions:
            extensions_not_found[ex] = DirectoryInfo('', 404, -1)
            rurl = "%s/HJR%s%s" %  (url, Tools.random_generator(10), ex)
            try:

                if url.endswith('/'):
                    url = url[:-1]

                r1 = requests.get("%s/HrandfileJR%s" % (url, ex), verify=False, timeout=30)

                r2 = requests.get(rurl, verify=False, timeout=30)

                if r1.status_code == r2.status_code:
                    extensions_not_found[ex] = DirectoryInfo('', r1.status_code, len(r1.text))
                else:
                    extensions_not_found[ex] = DirectoryInfo('', 404, -1)

            except Exception as e:

                extensions_not_found[ex] = DirectoryInfo('', 404, -1)

                if Configuration.verbose > 0:
                    Logger.pl('{*} {O}Error calculating default not found code to the folder %s: %s{W}' % (rurl, e))


            if Configuration.verbose > 4:
                Logger.pl('{?} {G}Checking not found: %s {O}%s - %d{W}' % (rurl, ex, extensions_not_found[ex]))


        '''Calculate and order by quantity'''
        codes = {}
        code_len = {}
        for ex, v in extensions_not_found.items():
            if v.dir_not_found in codes:
                codes[v.dir_not_found] += 1
            else:
                codes[v.dir_not_found] = 1

            if v.dir_not_found in code_len:
                if code_len[v.dir_not_found] > -1 and v.not_found_lenght != code_len[v.dir_not_found]:
                    code_len[v.dir_not_found] = -1
            else:
                code_len[v.dir_not_found] = v.not_found_lenght

        ret_item = max(codes.items(), key=operator.itemgetter(1))[0]

        return (ret_item, code_len[ret_item])

    def worker(self, index):
        try:
            while self.running:
                item = self.q.get()
                ret_ok = self.do_work(item)
                if ret_ok:
                    text = item.url.replace(Getter.base_url,"").lstrip("/").lstrip()
                    if not text == '':
                        self.last[index] = text
                    Getter.error_count = 0
                else:
                    Getter.error_count += 1

                self.q.task_done()
        except KeyboardInterrupt:
            pass

    def do_work(self, directory_info):

        self.add_checked()

        if Configuration.verbose > 4:
            Logger.pl('{?} {G}Starting worker to: {O}%s{W}' % directory_info.url)


        ret_ok =False  
        if not Getter.check_himself and directory_info.url == Getter.base_url:
            pass
        else:
            ret_ok = self.get_uri("%s/" % (directory_info.url), directory_info)
        for ex in Configuration.extensions:
            ret_ok = self.get_uri("%s%s" % (directory_info.url, ex), directory_info, False)

        return ret_ok
        

    def get_uri(self, url, directory_info, check_dir=True):

        ret_ok = False
        if Configuration.verbose > 4:
            Tools.clear_line()
            Logger.pl('{?} {G}Testing [%d/%d]: {O}%s{W}' % (Getter.checked,Getter.total,url))

        if not Configuration.full_log:
            Tools.clear_line()
            print(("Testing [%d/%d]: %s" % (Getter.checked,Getter.total,url)), end='\r', flush=True)

        try_cnt = 0
        while try_cnt < 5:
            try:

                r = requests.get(url, verify=False, timeout=30, allow_redirects=False)
                if r is not None and r.status_code > 0:
                    ret_ok = True

                if Configuration.full_log:
                    self.raise_url(url, r.status_code, len(r.text))
                else:
                    self.chech_if_rise(url, r.status_code, len(r.text), directory_info, check_dir)

                if Configuration.forward_location and (r.status_code == 302 or r.status_code == 301):
                    location = ''
                    try:
                        location = r.headers['Location']

                        if Configuration.verbose > 0:
                            Logger.pl('{*} {O}Forwarding to location %s from url %s{W}' % (location, url))

                        self.get_uri(location, DirectoryInfo(location, directory_info.dir_not_found, directory_info.not_found_lenght), check_dir)

                    except Exception as ef:

                        if Configuration.verbose > 0:
                            Tools.clear_line()
                            Logger.pl('{*} {O}Error forwarding to location %s from url %s: %s{W}' % (location, url, ef))
                        pass

                try_cnt = 4
            except Exception as e:

                Tools.clear_line()
                if Configuration.verbose > 1:
                    Logger.pl('{*} {O}Error loading %s: %s{W}' % (url, e))
                elif Configuration.verbose > 0:
                    Logger.pl('{*} {O}Error loading %s{W}' % url)
                pass

            if try_cnt >= 3:
                time.sleep( 0.2 * (try_cnt+1))
            try_cnt = try_cnt+1

            return ret_ok

    def chech_if_rise(self, url, status_code, size, directory_info, check_dir=True):

        if status_code in Configuration.ignore_rules:
            if False in Configuration.ignore_rules[status_code]:
                return
            elif size in Configuration.ignore_rules[status_code]:
                return

        
        if (status_code == directory_info.dir_not_found) and status_code != 404:

            if directory_info.not_found_lenght > 0 and (directory_info.not_found_lenght - 10) <= size <= (directory_info.not_found_lenght + 10):
                # E o codigo not found porem com tamanho diferente
                # esta tecnica visa pegar servidores que sempre retornam o mesmo status code
                self.raise_url(url, status_code, size)

            else:
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

        if status_code != directory_info.dir_not_found and status_code != 404:
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


class DirectoryInfo:

    url = ''
    dir_not_found = 404
    not_found_lenght = -1

    def __init__(self, url, dir_not_found, not_found_lenght=-1):
        self.url = url
        self.dir_not_found = dir_not_found
        self.not_found_lenght = not_found_lenght