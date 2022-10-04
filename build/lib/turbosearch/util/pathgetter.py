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
    duplicated=0
    last_item=""
    paused=True
    skip_current=False

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

                line = ''.join(filter(Tools.permited_char, line)).strip()

                if self.ingore_until == '' and line in self.last_start:
                    self.ingore_until = line     

                if Configuration.case_insensitive:
                    line = line.lower()

                if not Configuration.nudupcheck:
                    if line not in Configuration.words:
                        Configuration.words.append(line)
                        self.last_item = line
                    else:
                        self.duplicated+=1
                else:
                    Configuration.words.append(line)

                if Configuration.md5_search:
                    md5.update(line.strip().encode())
                    hash = md5.hexdigest()
                    Configuration.words.append(hash)
                    if Configuration.hash_upper:
                        Configuration.words.append(hash.upper())
                    
                if Configuration.sha1_search:
                    sha1.update(line.strip().encode())
                    hash = sha1.hexdigest()
                    Configuration.words.append(hash)
                    if Configuration.hash_upper:
                        Configuration.words.append(hash.upper())
                    
                if Configuration.sha256_search:
                    sha256.update(line.strip().encode())
                    hash = sha256.hexdigest()
                    Configuration.words.append(hash)
                    if Configuration.hash_upper:
                        Configuration.words.append(hash.upper())

                try:
                    line = f.readline()
                except:
                    pass

        if Configuration.doublepath:
            c = len(Configuration.words) * len(Configuration.words)
            c1 = 0
            Logger.pl('     {*} {W}Calculating double path. Estimating {O}%d{W} more additional paths at wordlist. Be patient.{W}' % (c))

            # Clone array
            tmp = Configuration.words[:]

            for p1 in tmp:
                for p2 in tmp:
                    c1 += 1
                    Configuration.words.append(f"{p1}/{p2}".strip(" /\\"))
                    Tools.clear_line()
                    print(('Adding double path [%d/%d]' % (c1,c)), end='\r', flush=True)

            Tools.clear_line()

    def len(self):
        return len(Configuration.words)


    def run(self):

        t = threading.Thread(target=self.worker)
        t.daemon = True
        t.start()

        t_status = threading.Thread(target=self.status_worker)
        t_status.daemon = True
        t_status.start()

        count = 0
        with self.q.mutex:
            self.q.queue.clear()

        if self.current_uri != '':
            insert = False
            for u in self.added:
                if not insert and u == self.current_uri:
                    insert = True

                if insert and self.skip_current:
                    self.skip_current = False
                elif insert:
                    count += 1
                    self.q.put(u)
        else:
            count += 1
            self.added.append(Configuration.target)
            self.q.put(Configuration.target)


        #if len(list(self.q.queue)) > 0:
        if (count > 0):
            self.paused=False

            self.q.join()  # block until all tasks are done
            sys.stdout.write("\033[K")  # Clear to the end of line

    def worker(self):
        try:
            while self.running:

                while self.paused:
                    time.sleep(0.3)

                item = self.q.get()

                if item != Configuration.target:
                    Logger.pl('  ')
                    Logger.pl('{+} {W}Entering directory: {C}%s{W} ' % item)

                self.current_uri = item
                self.current_gettter = Getter(Configuration.words, False)
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

                if Configuration.verbose > 3:
                    Logger.pl('{*} {W}Finishing %s{W}' % (item))


                self.ingore_until = ''
                self.q.task_done()
        except KeyboardInterrupt as e:
            raise e

    def testing_base(self):
        return self.current_uri == Configuration.target

    def pause(self):
        self.paused=True
        self.running=False
        self.save_status()
        self.current_gettter.pause()
        
        
    def skip(self):
        self.ingore_until = ''
        self.save_status(True)
        self.running=False
        self.paused=False
        self.current_gettter.stop()
        with self.q.mutex:
            self.q.queue.clear()


    def save_status(self, skip_current=False):
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
        "skip_current" : skip_current,
        "paths": self.added,
        "deep_links": Getter.deep_links,
        "threads": self.current_gettter.last 
         }

        with open("turbosearch.restore", "w") as text_file:
            text_file.write(json.dumps(dt))

    def status_worker(self):
        try:
            while self.running:
                try:
                    if self.current_gettter is None:
                        time.sleep(1)
                        continue

                    if self.paused:
                        time.sleep(1)
                        continue

                    self.save_status()

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
            

