#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from ..util.tools import Tools

import os, subprocess, socket, re, requests, queue, threading, sys, operator, time, json

from ..config import Configuration
from ..util.logger import Logger
from bs4 import BeautifulSoup
from urllib.parse import urlparse


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
    deep_links = []


    '''Local non-static variables'''
    q = queue.Queue()
    words = []
    base_url = ''
    last = {}
    running=True
    proxy={}
    paused=False

    def __init__(self, words_list, check_himself = True):
        self.words = words_list
        Getter.check_himself = check_himself
        Getter.checked = 0
        Getter.total = 0
        Getter.ingore_until = ''
        Getter.dir_not_found = 404
        Getter.not_found_lenght = -1
        Getter.path_found = []
        Getter.running=True

        requests.packages.urllib3.disable_warnings()

        Getter.proxy={}
        if Configuration.proxy != '':
            Getter.proxy = {
              'http': Configuration.proxy,
              'https': Configuration.proxy,
            }
        

        pass

    def pause(self):
        Getter.paused=True

    def add_checked(self):
        if Getter.checked < Getter.total:
            Getter.checked += 1

    def stop(self):
        Getter.running=False

    def run(self, base_url):
        Getter.paused = False
        Getter.running=True
        Getter.path_found = []
        Getter.base_url = base_url

        if Getter.base_url.endswith('/'):
            Getter.base_url = Getter.base_url [:-1]

        (Getter.dir_not_found, Getter.not_found_lenght) = Getter.calc_not_fount(Getter.base_url)

        if Getter.not_found_lenght > 0:
            Logger.pl('{*} {W}Calculated default not found http code, using GET, for this folder is {O}%d{W} with content size {O}%d{W}' % (Getter.dir_not_found, Getter.not_found_lenght))
        else:
            Logger.pl('{*} {W}Calculated default not found http code, using GET, for this folder is {O}%d{W} with no content' % (Getter.dir_not_found))

        for i in range(Configuration.tasks):
            self.last[i] = ''
            t = threading.Thread(target=self.worker, kwargs=dict(index=i))
            t.daemon = True
            t.start()

        insert = True
        if self.ingore_until != '':
            insert = False

        with self.q.mutex:
            self.q.queue.clear()

        if Configuration.deep and Configuration.target == base_url:
            self.q.put(DirectoryInfo("%s/" % (Getter.base_url), Getter.dir_not_found, Getter.not_found_lenght))
                
        Getter.total = len(self.words)    
        for item in self.words:
            if Getter.running and item.strip() != '':
                if not insert and item == self.ingore_until:
                    insert = True

                if insert:
                    self.q.put(DirectoryInfo("%s/%s" % (Getter.base_url, item), Getter.dir_not_found, Getter.not_found_lenght))
                else:
                    self.add_checked()

        #self.q.join()  # block until all tasks are done

        while(Getter.running):
            if len(self.q.queue) > 0:

                if Configuration.verbose > 5:
                    Logger.pl('{?} {G}Queue len: {O}%s{W}' % len(self.q.queue))

                time.sleep(0.3)
            else:
                Getter.running=False
        Tools.clear_line()

        return Getter.path_found

    @staticmethod
    def general_request(url, proxy=None, force_method=None):

        headers = {}

        headers = Configuration.user_headers
        if Configuration.user_agent:
            headers['User-Agent'] = Configuration.user_agent
        
        if force_method is None:
            if len(Configuration.request_methods) > 0:
                method = Configuration.request_methods[0]
            else:
                method = "GET"
        else:
            method = force_method.upper()

        if method == "POST":
            return requests.post(url, verify=False, timeout=30, data={}, headers=headers, proxies=(proxy if proxy!=None else Getter.proxy))
        elif method == "PUT":
            return requests.put(url, verify=False, timeout=30, data={}, headers=headers, proxies=(proxy if proxy!=None else Getter.proxy))
        elif method == "OPTIONS":
            return requests.options(url, verify=False, timeout=30, headers=headers, proxies=(proxy if proxy!=None else Getter.proxy))
        elif method == "HEAD":
            return requests.head(url, verify=False, timeout=30, headers=headers, proxies=(proxy if proxy!=None else Getter.proxy))
        elif method == "PATCH":
            return requests.patch(url, verify=False, timeout=30, headers=headers, proxies=(proxy if proxy!=None else Getter.proxy))
        else:
            return requests.get(url, verify=False, timeout=30, headers=headers, proxies=(proxy if proxy!=None else Getter.proxy))
        
    @staticmethod
    def calc_not_fount(url):

        extensions_not_found = {}
        extensions_not_found["__root__"] = DirectoryInfo('', 404, -1)

        try:

            if url.endswith('/'):
                url = url[:-1]

            r1 = Getter.general_request("%s/HrandfileJR" % (url))

            r2 = Getter.general_request("%s/HJR%s" % (url, Tools.random_generator(10)))

            if r1 is not None and r2 is not None and r1.status_code == r2.status_code:
                extensions_not_found["__root__"] =  DirectoryInfo('', r1.status_code, len(r1.text))
            else:
                extensions_not_found["__root__"] = DirectoryInfo('', 404, -1)

        except Exception as e:
            extensions_not_found["__root__"] = DirectoryInfo('', 404, -1)

            if Configuration.verbose > 0:
                Logger.pl('{*} {O}Error calculating default not found code to the folder %s: %s{W}' % (url, e))


        if Configuration.verbose > 4:
            Logger.pl('{?} {G}Checking not found: %s {O}%s - %s{W}' % (url, "__root__", extensions_not_found["__root__"]))


        for ex in Configuration.extensions:
            extensions_not_found[ex] = DirectoryInfo('', 404, -1)
            rurl = "%s/HJR%s%s" %  (url, Tools.random_generator(10), ex)
            try:

                if url.endswith('/'):
                    url = url[:-1]

                r1 = Getter.general_request("%s/HrandfileJR%s" % (url, ex))

                r2 = Getter.general_request(rurl)

                if r1 is not None and r2 is not None and r1.status_code == r2.status_code:
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
            while Getter.running:

                while Getter.paused:
                    time.sleep(1)
                    if not Getter.running:
                        return

                item = self.q.get()
                try:
                    ret_ok = self.do_work(item)
                    if ret_ok:
                        text = item.url.replace(Getter.base_url,"").lstrip("/").lstrip()
                        if not text == '':
                            self.last[index] = text
                        Getter.error_count = 0
                    else:
                        Getter.error_count += 1
                except KeyboardInterrupt as e:
                    raise e
                finally:
                    self.q.task_done()

        except KeyboardInterrupt as e:
            raise e

    def do_work(self, directory_info):

        self.add_checked()

        if Configuration.verbose > 4:
            Logger.pl('{?} {G}Starting worker to: {O}%s{W}' % directory_info.url)


        ret_ok = False  
        if not Getter.check_himself and directory_info.url == Getter.base_url:
            ret_ok = True
        else:
            ret_ok = self.get_uri("%s/" % (directory_info.url), directory_info)
        for ex in Configuration.extensions:
            ret_ok = self.get_uri("%s%s" % (directory_info.url, ex), directory_info, False)

        return ret_ok
        
    def get_uri(self, url, directory_info, check_dir=True, deep_level=0):

        if Getter.paused or not Getter.running:
            return

        ret_ok = False 

        for m in Configuration.request_methods:
            r1 = self.get_uri_internal(url, directory_info, check_dir, deep_level, m)
            if r1:
                ret_ok = True
    
        return ret_ok


    def get_uri_internal(self, url, directory_info, check_dir=True, deep_level=0, force_method=None):

        if Getter.paused or not Getter.running:
            return

        if url.endswith('/'):
            while url.endswith('/'):
                url = url[:-1]
            url += "/"

        ret_ok = False
        if Configuration.verbose > 4:
            Tools.clear_line()
            Logger.pl('{?} {G}Testing [%d/%d]: {O}%s{W}' % (Getter.checked,Getter.total,url))


        if not Configuration.full_log:
            Tools.clear_line()
            print(("Testing [%d/%d]: %s" % (Getter.checked,Getter.total,url)), end='\r', flush=True)
            pass
        
        try_cnt = 0
        while try_cnt < 5:
            try:

                r = Getter.general_request(url, force_method=force_method)
                if r is not None and r.status_code > 0:
                    ret_ok = True

                Tools.check_content(r);

                if Configuration.full_log or Configuration.verbose > 4:
                    self.raise_url(url, r.status_code, len(r.text), r.request.method)
                else:
                    self.chech_if_rise(url, r.status_code, len(r.text), r.request.method, directory_info, check_dir)

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

                if deep_level <= 5:
                    self.deep_link(r, directory_info, check_dir, deep_level)


                try_cnt = 4
            except Exception as e:

                Tools.clear_line()
                if Configuration.verbose > 1:
                    Logger.pl('{*} {O}Error loading %s: %s{W}' % (url, e))
                    sys.exit(0)
                elif Configuration.verbose > 0:
                    Logger.pl('{*} {O}Error loading %s{W}' % url)
                pass

            if try_cnt >= 3:
                time.sleep( 0.2 * (try_cnt+1))
            try_cnt = try_cnt+1

            return ret_ok

    def chech_if_rise(self, url, status_code, size, method, directory_info, check_dir=True):

        if status_code in Configuration.ignore_rules:
            if False in Configuration.ignore_rules[status_code]:
                if Configuration.verbose > 0:
                    Logger.pl('{*} {O}Ignoring result to location %s with status code %s and size %s{W}' % (url,status_code,size))
                return
            elif size in Configuration.ignore_rules[status_code]:
                if Configuration.verbose > 0:
                    Logger.pl('{*} {O}Ignoring result to location %s with status code %s and size %s{W}' % (url,status_code,size))
                return

        if (status_code == directory_info.dir_not_found) and status_code != 404:

            if directory_info.not_found_lenght > 0 and (size <= (directory_info.not_found_lenght - 10) or size >= (directory_info.not_found_lenght + 10)):
                # E o codigo not found porem com tamanho diferente
                # esta tecnica visa pegar servidores que sempre retornam o mesmo status code
                self.raise_url(url, status_code, size, method)

            else:
                '''Double check'''
                r2 = Getter.general_request(url + '_')
                if r2 is not None and status_code != r2.status_code:
                    #self.raise_url(url, r2.status_code, size)
                    self.raise_url(url, status_code, size, method)
                    return

                '''else:
                    if url.endswith('/') and check_dir:
                        r2 = Getter.general_request(url[:-1])
                        if r.status_code != r2.status_code:
                            self.raise_url(url, r2.status_code, len(r2.text))
                        elif  len(r2.text) - 50 <= len(r.text) <= len(r2.text) + 50:
                            self.raise_url(url, r2.status_code, len(r2.text))'''

        if status_code != directory_info.dir_not_found and status_code != 404:
            #if url.endswith('/') and check_dir:
            #    tmp_nf = Getter.calc_not_fount(url)
            #    self.chech_if_rise(url, status_code, size, tmp_nf, False)
            #else:
            self.raise_url(url, status_code, size, method)

    def raise_url(self, url, status, len, method):

        if url.endswith('/'):
            '''if status == 403:'''
            Logger.pl('==> DIRECTORY: %s (METHOD:%s|CODE:%d|SIZE:%d)' % (
            url, method, status, len))
            Getter.path_found.append(url)
            '''else:
            Logger.pl('==> DIRECTORY: %s ' % url)
            Getter.path_found.append(url)'''
        else:
            Logger.pl('+ %s (CODE:%d|SIZE:%d) ' % (
                url, status, len))

        try:
            if Configuration.db is not None:
                Configuration.db.insertUri(url, status, len)
        except:
            pass

        if Configuration.proxy_report_to != '':
            try:
                proxy={}

                proxy = {
                  'http': Configuration.proxy_report_to,
                  'https': Configuration.proxy_report_to,
                }
                
                Getter.general_request(url, proxy)

            except Exception as e:
                pass

    def deep_link(self, result, directory_info, check_dir, deep_level):
        if Configuration.deep:
            rUri = urlparse(result.request.url)
            soup = BeautifulSoup(result.text, "html.parser" )
            links = soup.find_all('a')
            for tag in links:
                link = tag.get('href',None)
                if link is not None:
                    l1 = link

                    if l1.find("javascript") != -1:
                        continue
                    if l1.find("aboult:") == 0:
                        continue
                    if l1.find("#") == 0:
                        continue
                    if l1.find("mail") == 0:
                        continue

                    if l1.endswith('.pdf'):
                        continue
                    if l1.endswith('.exe'):
                        continue
                    if l1.endswith('.png'):
                        continue
                    if l1.endswith('.jpg'):
                        continue
                    if l1.endswith('.gif'):
                        continue
                    if l1.endswith('.bin'):
                        continue

                    if l1.find("//") == 0:
                        l1 = "%s:%s" % (rUri.scheme, l1)
                    elif l1.find("/") == 0:
                        l1 = "%s://%s%s" % (rUri.scheme, rUri.netloc, l1)
                    elif l1.find("://") == -1:

                        #calculate directory
                        path = rUri.path
                        if not path.endswith('/'):
                            parts = path.split("/")
                            parts = parts[:-1]
                            path = '/'.join(parts)

                        l1 = "%s://%s%s/%s" % (rUri.scheme, rUri.netloc, path.rstrip("/"), l1)

                    checked = True if l1 in Getter.deep_links else False

                    if checked:
                        continue


                    #Logger.pl("1.%d: %s" % (deep_level, l1))
                    
                    pl1 = urlparse(l1)
                    if pl1.netloc.lower() == rUri.netloc.lower():
                        #Getter.deep_links.append(l1)

                        # Parse para identificar diretórios
                        url_base = "%s://%s" % (pl1.scheme, pl1.netloc)
                        path = ""
                        parts = pl1.path.split("/")
                        for p in parts:
                            if p != "":
                                path += "/" + p
                                p1 = "%s%s" % (url_base,path)
                                p2 = "%s%s/" % (url_base,path)
                                
                                if pl1.path == path:
                                    #print(l1, p1)
                                    if p1 not in Getter.deep_links:
                                        Getter.deep_links.append(p1)
                                        self.get_uri(p1, directory_info, check_dir, deep_level + 1)
                                    
                                if p.find(".") == -1 and p2 not in Getter.deep_links:
                                    Getter.deep_links.append(p2)
                                    self.get_uri(p2, directory_info, check_dir, deep_level + 1)


                    else:
                        i1 = True if l1 not in Getter.deep_links else False
                        if i1:
                            Getter.deep_links.append(l1)
                            Logger.pl('==> EXTERNAL LINK: %s' % (l1))
                    
                    
class DirectoryInfo:

    url = ''
    dir_not_found = 404
    not_found_lenght = -1

    def __init__(self, url, dir_not_found, not_found_lenght=-1):
        self.url = url
        self.dir_not_found = dir_not_found
        self.not_found_lenght = not_found_lenght