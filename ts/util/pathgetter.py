#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from ..util.tools import Tools

import os, subprocess, socket, re, queue, threading, sys, time, json, hashlib

from ..config import Configuration
from ..util.logger import Logger
from ..util.getter import Getter

class PathGetter:

    words = []
    q = queue.Queue()
    added = []
    last_start = []
    ingore_until = ''
    current_gettter = None
    current_uri = ''
    running=True

    def __init__(self):
        pass

    def load_wordlist(self):

        if Configuration.threads_data is not None:
            try:
                for i in Configuration.threads_data:
                    self.last_start.append(Configuration.threads_data[i])
            except:
                pass

        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()

        with open(Configuration.word_list, 'r', encoding="ascii", errors="surrogateescape") as f:
            line = f.readline()
            while line:
                if line.endswith('\n'):
                    line = line[:-1]
                if line.endswith('\r'):
                    line = line[:-1]

                line = ''.join(filter(self.permited_char, line))

                if self.ingore_until == '' and line in self.last_start:
                    self.ingore_until = line     

                self.words.append(line.strip())


                if Configuration.md5_search:
                    md5.update(line.strip().encode())
                    hash = md5.hexdigest()
                    self.words.append(hash)
                    if Configuration.hash_upper:
                        self.words.append(hash.upper())
                    
                if Configuration.sha1_search:
                    sha1.update(line.strip().encode())
                    hash = sha1.hexdigest()
                    self.words.append(hash)
                    if Configuration.hash_upper:
                        self.words.append(hash.upper())
                    
                if Configuration.sha256_search:
                    sha256.update(line.strip().encode())
                    hash = sha256.hexdigest()
                    self.words.append(hash)
                    if Configuration.hash_upper:
                        self.words.append(hash.upper())

                    

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


        t_status = threading.Thread(target=self.status_worker)
        t_status.daemon = True
        t_status.start()

        if self.current_uri != '':
            insert = False
            for u in self.added:
                if not insert and u == self.current_uri:
                    insert = True
                if insert:
                    self.q.put(u)
        else:
            self.added.append(Configuration.target)
            self.q.put(Configuration.target)

        self.q.join()  # block until all tasks are done
        sys.stdout.write("\033[K")  # Clear to the end of line


    def worker(self):
        try:
            while self.running:
                item = self.q.get()

                if item != Configuration.target:
                    Logger.pl('  ')
                    Logger.pl('{+} {W}Entering directory: {C}%s{W} ' % item)

                self.current_uri = item
                self.current_gettter = Getter(self.words, False)
                self.current_gettter.ingore_until = self.ingore_until
                paths_found = self.current_gettter.run(item)

                if Configuration.verbose > 0:
                    Logger.pl('{*} {W}We got {O}%d{W} new directories to check from url %s{W}' % (len(paths_found), item))

                for u in paths_found:
                    if u.endswith('/'):
                        u = u[:-1]
                    if u not in self.added:
                        self.added.append(u)
                        self.q.put(u)

                self.ingore_until = ''
                self.q.task_done()
        except KeyboardInterrupt:
            pass


    def status_worker(self):
        try:
            while True:
                try:
                    if self.current_gettter is None:
                        time.sleep(1)
                        continue

                    paths_found = self.current_gettter.path_found

                    for u in paths_found:
                        if u.endswith('/'):
                            u = u[:-1]
                        if u not in self.added:
                            self.added.append(u)
                            self.q.put(u)


                    dt = { 
                    "command" : Configuration.cmd_line,
                    "current_path" : self.current_uri,
                    "paths": self.added,
                    "deep_links": Getter.deep_links,
                    "threads": self.current_gettter.last 
                     }

                    with open("turbosearch.restore", "w") as text_file:
                        text_file.write(json.dumps(dt))

                    if Getter.error_count >= 50:
                        self.current_gettter.stop()
                        self.running=False
                        Tools.clear_line()
                        Logger.pl('\r\n{!} {R}FATAL: Too many errors connecting to host, exiting...{W}')
                        Logger.pl('     {O}you can use \'turbosearch -R\' to restore/continue this session{W}\r\n')
                        Configuration.kill(0)

                except:
                    raise
                time.sleep(10)
        except KeyboardInterrupt:
            pass
            

