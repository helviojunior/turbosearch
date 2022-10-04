#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os, subprocess, socket, re, requests, errno, sys, time, json, signal, base64, hashlib, random
from pathlib import Path

from .args import Arguments
from .util.color import Color
from .util.logger import Logger
from .util.database import Database
from .version import __version__

class Configuration(object):
    ''' Stores configuration variables and functions for Turbo Search. '''
    version = '0.0.0'

    initialized = False # Flag indicating config has been initialized
    verbose = 0
    target = ''
    word_list = ''
    out_file = ''
    extensions = []
    full_log = False
    forward_location = True
    cmd_line =''
    restore = ''
    ignore = ''
    threads_data = None
    restored_uri=''
    restored_paths=[]
    restored_deep_links=[]
    threads_data={}
    md5_search = False
    sha1_search = False
    sha256_search = False
    hash_upper = False
    deep = False
    ignore_rules={}
    proxy=''
    proxy_report_to=''
    text_to_find = []
    available_methods=['GET', 'POST', 'PUT', 'PATCH', 'HEAD', 'OPTIONS']
    request_methods=['GET']
    user_agent=''
    user_headers={}
    case_insensitive=False
    words=[]
    skip_current=False
    db = None
    statsdb=False
    norobots = False
    nudupcheck = False
    doublepath = False

    @staticmethod
    def initialize():
        '''
            Sets up default initial configuration values.
            Also sets config values based on command-line arguments.
        '''

        # Only initialize this class once
        if Configuration.initialized:
            return
        Configuration.initialized = True

        Configuration.verbose = 0 # Verbosity level.
        Configuration.print_stack_traces = True

        # Overwrite config values with arguments (if defined)
        Configuration.load_from_arguments()


    @staticmethod
    def load_from_arguments():
        ''' Sets configuration values based on Argument.args object '''
        from .args import Arguments

        config_check = 0

        force_restore = any(['-R' in word for word in sys.argv])
        help = any(['-h' in word for word in sys.argv])

        if help:
            args = Arguments().args
        else:
            if not force_restore and os.path.exists("turbosearch.restore"):
                ignore = any(['-I' in word for word in sys.argv])
                if not ignore:
                    Color.pl('{!} {W}Restorefile (you have 10 seconds to abort... (use option -I to skip waiting)) from a previous session found, to prevent overwriting, ./turbosearch.restore')
                    time.sleep(10)
                os.remove("turbosearch.restore")

            args = {}
            if os.path.exists("turbosearch.restore"):
                try:
                    with open("turbosearch.restore", 'r') as f:
                        restore_data = json.load(f)
                        Configuration.cmd_line = restore_data["command"]
                        Configuration.threads_data = restore_data["threads"]
                        Configuration.restored_uri = restore_data["current_path"]
                        Configuration.restored_paths = restore_data["paths"]
                        Configuration.restored_deep_links = restore_data["deep_links"]
                        Configuration.skip_current = restore_data.get("skip_current",False)

                except Exception as e:
                    Color.pl('{!} {R}error: invalid restore file\r\n')
                    raise

                args = Arguments(Configuration.cmd_line).args

            else:
                args = Arguments().args
                for a in sys.argv:
                    if a != "-I":
                        Configuration.cmd_line += "%s " % a



        Color.pl('{+} {W}Startup parameters')

        Logger.pl('     {C}command line:{O} %s{W}' % Configuration.cmd_line)

        if args.target:
            Configuration.target = args.target
            if Configuration.target.endswith('/'):
                Configuration.target = Configuration.target[:-1]

        if args.tasks:
            Configuration.tasks = args.tasks

        if args.word_list:
            Configuration.word_list = args.word_list

        if args.verbose:
            Configuration.verbose = args.verbose

        if args.out_file:
            Configuration.out_file = args.out_file

        if args.tasks:
            Configuration.tasks = args.tasks

        if Configuration.tasks < 1:
            Configuration.tasks = 1

        if Configuration.tasks > 256:
            Configuration.tasks = 256

        if Configuration.target == '':
            config_check = 1

        if Configuration.word_list == '':
            config_check = 1

        if config_check == 1:
            Configuration.mandatory()

        if args.full_log:
            Configuration.full_log = args.full_log

        if args.no_forward_location:
            Configuration.forward_location = False

        if args.md5_search:
            Configuration.md5_search = True

        if args.sha1_search:
            Configuration.sha1_search = True

        if args.sha256_search:
            Configuration.sha256_search = True

        if args.hash_upper:
            Configuration.hash_upper = True

        if args.deep:
            Configuration.deep = True

        if args.proxy:
            Configuration.proxy = args.proxy

        if args.statsdb:
            Configuration.statsdb = args.statsdb

        if args.report_to:
            Configuration.proxy_report_to = args.report_to

        if args.doublepath:
            Configuration.doublepath = args.doublepath

        if args.nudupcheck:
            Configuration.nudupcheck = True


        if args.request_method != '':
            if args.request_method.upper().strip() == "ALL":
                Configuration.request_methods = Configuration.available_methods
            else:
                Configuration.request_methods = []
                m_list = (args.request_method + ",").split(",")
                for m in m_list:
                    m1 = m.strip().upper()
                    if m1 != '' and m1 not in Configuration.request_methods and m1 in Configuration.available_methods:
                        Configuration.request_methods.append(m1)

        if len( Configuration.request_methods) == 0:
            Logger.pl('{!} {R}error: could not parse valid request method(s) from value {O}%s{R} {W}\r\n' % (args.request_method))
            Configuration.exit_gracefully(0)

        if args.case_insensitive:
            Configuration.case_insensitive = args.case_insensitive

        if args.norobots:
            Configuration.norobots = args.norobots

        if args.random_agent:
            try:
                
                with open(str(Path(__file__).parent) + "/resources/user_agents.txt", 'r') as f:
                    # file opened for writing. write to it here
                    line = next(f)
                    for num, aline in enumerate(f, 2):
                        if random.randrange(num):
                            continue
                        if aline.strip("\r\n").strip() == '':
                            continue
                        Configuration.user_agent = aline.strip("\r\n").strip()
                    
            except IOError as x:
                if x.errno == errno.EACCES:
                    Color.pl('{!} {R}error: could not open ./resources/user_agents.txt {O}permission denied{R}{W}\r\n')
                    Configuration.exit_gracefully(0)
                elif x.errno == errno.EISDIR:
                    Color.pl('{!} {R}error: could not open ./resources/user_agents.txt {O}it is an directory{R}{W}\r\n')
                    Configuration.exit_gracefully(0)
                else:
                    Color.pl('{!} {R}error: could not open ./resources/user_agents.txt{W}\r\n')
                    Configuration.exit_gracefully(0)

        if args.header != '':
            jData = {}
            try:
                jData=json.loads(args.header)
            except:
                Logger.pl('{!} {R}error: could not convert header value {O}%s{R} from an JSON object {W}\r\n' % (args.header))
                Configuration.exit_gracefully(0)

            Configuration.user_headers={}
            try:
                for k in jData:
                    if isinstance(k, str):
                        if isinstance(jData[k], str):
                            if k.lower().find("user-agent") != -1:
                                Configuration.user_agent  = jData[k]
                            elif k.lower().find("host") != -1:
                                pass
                            elif k.lower().find("connection") != -1:
                                pass
                            elif k.lower().find("accept") != -1:
                                pass
                            elif k.lower().find("accept-encoding") != -1:
                                pass
                            else:
                                Configuration.user_headers[k] = jData[k]
                        else:
                            raise Exception("The value of %s id not an String" % k)
                    else:
                        raise Exception("%s id not an String" % k)
            except Exception as e:
                Logger.pl('{!} {R}error: could parse header data: {R}%s{W}\r\n' % (str(e)))
                Configuration.exit_gracefully(0)

        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, Configuration.target) is None:
            Color.pl('{!} {R}error: invalid target {O}%s{R}{W}\r\n' % Configuration.target)
            Configuration.exit_gracefully(0)

        if Configuration.proxy != '' and re.match(regex, Configuration.proxy) is None:
            Color.pl('{!} {R}error: invalid proxy {O}%s{R}{W}\r\n' % Configuration.proxy)
            Configuration.exit_gracefully(0)

        if Configuration.proxy_report_to != '' and re.match(regex, Configuration.proxy_report_to) is None:
            Color.pl('{!} {R}error: invalid report to proxy {O}%s{R}{W}\r\n' % Configuration.proxy_report_to)
            Configuration.exit_gracefully(0)

        if not os.path.isfile(Configuration.word_list):
            Color.pl('{!} {R}error: word list file not found {O}%s{R}{W}\r\n' % Configuration.word_list)
            Configuration.exit_gracefully(0)

        if Configuration.out_file != '':
            try:
                with open(Configuration.out_file, 'a', encoding="utf-8") as f:
                    # file opened for writing. write to it here
                    Logger.out_file = Configuration.out_file
                    f.write(Color.sc(Configuration.get_banner()) + '\n')
                    f.write(Color.sc('{+} {W}Startup parameters') + '\n')
                    pass
            except IOError as x:
                if x.errno == errno.EACCES:
                    Color.pl('{!} {R}error: could not open output file to write {O}permission denied{R}{W}\r\n')
                    Configuration.exit_gracefully(0)
                elif x.errno == errno.EISDIR:
                    Color.pl('{!} {R}error: could not open output file to write {O}it is an directory{R}{W}\r\n')
                    Configuration.exit_gracefully(0)
                else:
                    Color.pl('{!} {R}error: could not open output file to write{W}\r\n')
                    Configuration.exit_gracefully(0)


        try:
            with open(Configuration.word_list, 'r') as f:
                # file opened for writing. write to it here
                pass
        except IOError as x:
            if x.errno == errno.EACCES:
                Logger.pl('{!} {R}error: could not open word list file {O}permission denied{R}{W}\r\n')
                Configuration.exit_gracefully(0)
            elif x.errno == errno.EISDIR:
                Logger.pl('{!} {R}error: could not open word list file {O}it is an directory{R}{W}\r\n')
                Configuration.exit_gracefully(0)
            else:
                Logger.pl('{!} {R}error: could not open word list file {W}\r\n')
                Configuration.exit_gracefully(0)


        Logger.pl('     {C}target:{O} %s{W}' % Configuration.target)

        if Configuration.proxy != '':
            Logger.pl('     {C}Proxy:{O} %s{W}' % Configuration.proxy)

        Logger.pl('     {C}tasks:{O} %s{W}' % Configuration.tasks)

        if args.verbose:
            Logger.pl('     {C}option:{O} verbosity level %d{W}' % Configuration.verbose)

        Logger.pl('     {C}request method(s): {O}%s{W}' % ', '.join(Configuration.request_methods))

        if Configuration.user_agent:
            Logger.pl('     {C}user agent: {O}%s{W}' % Configuration.user_agent)

        Logger.pl('     {C}word list:{O} %s{W}' % Configuration.word_list)

        if Configuration.doublepath:
            Logger.pl('     {C}double path search:{O} yes{W}')

        if Configuration.forward_location:
            Logger.pl('     {C}forward location redirects:{O} yes{W}')

        if Configuration.deep:
            Logger.pl('     {C}deep links search:{O} yes{W}')

        if Configuration.case_insensitive:
            Logger.pl('     {C}case insensitive search:{O} yes{W}')
        else:
            Logger.pl('     {C}case insensitive search:{O} no{W}')


        if args.extensions != '':
            ext_list = args.extensions.split(",")
            for ex in ext_list:
                ex1 = ex.strip()
                if ex1 != '' and ex1 not in Configuration.extensions:
                    Configuration.extensions.append(ex.strip())

        ext_txt = ''
        if len(Configuration.extensions) > 0:
            ext_txt = ''
            for ex in Configuration.extensions:
                ext_txt += '(%s)' % ex

        if ext_txt != '':
            Logger.pl('     {C}extension list:{O} %s{W}' % ext_txt)

        if Configuration.out_file != '':
            Logger.pl('     {C}output file:{O} %s{W}' % Configuration.out_file)


        if args.filter_rules != '':
            ignore_list = args.filter_rules.split(",")
            for ignore_line in ignore_list:
                ignore_line = ignore_line.strip()
                if ':' in ignore_line:
                    (i_result,i_size) = ignore_line.split(":")
                    size=0
                    res=0
                    try:
                        res=int(i_result)
                    except:
                        Logger.pl('{!} {R}error: could not convert {O}%s{R} from {O}%s{R} to an integer value {W}\r\n' % (i_result,ignore_line))
                        Configuration.exit_gracefully(0)

                    try:
                        size=int(i_size)
                    except:
                        Logger.pl('{!} {R}error: could not convert {O}%s{R} from {O}%s{R} to an integer value {W}\r\n' % (i_size,ignore_line))
                        Configuration.exit_gracefully(0)
                    
                    if not res in Configuration.ignore_rules:
                        Configuration.ignore_rules[res] = []
                    Configuration.ignore_rules[res].append(size)

                else:
                    res=0
                    try:
                        res=int(ignore_line)
                    except:
                        Logger.pl('{!} {R}error: could not convert {O}%s{R} to an integer value {W}\r\n' % (ignore_line))
                        Configuration.exit_gracefully(0)

                    if not res in Configuration.ignore_rules:
                        Configuration.ignore_rules[res] = []
                    Configuration.ignore_rules[res].append(False)


        if Configuration.statsdb:
            try:
                Configuration.db = Database()
            except Exception as e:
                Logger.pl('{!} {R}error: could not create stats database {R}%s{W}\r\n' % (str(e)))
                Configuration.exit_gracefully(0)

        if args.find != '':
            tmp_find_lst = []
            find_list = args.find.split(",")
            for ex in find_list:
                ex1 = ex.strip()
                if ex1 != '' and ex1 not in tmp_find_lst:
                    tmp_find_lst.append(ex1)
                    
            if len(tmp_find_lst) > 0:
                fnd_txt = ''
                for ex in tmp_find_lst:
                    fnd_txt += '(%s)' % ex

            if fnd_txt != '':
                Logger.pl('     {C}find list:{O} %s{W}' % ext_txt)

            if len(tmp_find_lst) > 0:
                md5 = hashlib.md5()
                sha1 = hashlib.sha1()
                sha256 = hashlib.sha256()
                    
                for fndw in tmp_find_lst:
                    words = []
                    words.append(fndw)
                    
                    if fndw.upper() not in words:
                        words.append(fndw.upper())
                    if fndw.lower() not in words:
                        words.append(fndw.lower())                    

                    for ex in words:
                        if ex not in Configuration.text_to_find:
                            Configuration.text_to_find.append(ex)
                    
                        md5.update(ex.encode())
                        hash = md5.hexdigest()
                        if hash not in Configuration.text_to_find:
                            Configuration.text_to_find.append(hash)
                            Configuration.text_to_find.append(hash.upper())
                            
                        sha1.update(ex.encode())
                        hash = sha1.hexdigest()
                        if hash not in Configuration.text_to_find:
                            Configuration.text_to_find.append(hash)
                            Configuration.text_to_find.append(hash.upper())
                            
                        sha256.update(ex.encode())
                        hash = sha256.hexdigest()
                        if hash not in Configuration.text_to_find:
                            Configuration.text_to_find.append(hash)
                            Configuration.text_to_find.append(hash.upper())
                            
                        encoded = base64.b64encode(ex.encode()).decode()
                        encoded = encoded.replace('=','')
                        if encoded not in Configuration.text_to_find:
                            Configuration.text_to_find.append(encoded)
                    

    @staticmethod
    def variants(word):
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()    
        words = []
        if word not in words:
            words.append(word)
        
        if word.upper() not in words:
            words.append(word.upper())
        
        if word.upper() not in words:
            words.append(word.lower())

        for ex in words:
            encoded = base64.b64encode(ex.encode()).decode()
            encoded = encoded.replace('=','')
            if encoded not in Configuration.text_to_find:
                Configuration.text_to_find.append(encoded)

    @staticmethod
    def get_banner():
            """ Displays ASCII art of the highest caliber.  """

            Configuration.version = str(__version__)

            return '''\

{G}HHHHHH{W}           {R}→→{G}HHH{W}
{G}HHHHHH{W}           {R}→→→→{G}HH{W}            
{G}HHHHHH{W}           {R}→→→→→→{W}
{R}→→{W}-{R}→→→→→→→→→→→→→→→→→→→→→→          {G}Turbo Search {D}v%s{W}{G} by Helvio Junior{W}
{R}→→{W}|{R}→→→→→→→→→→→→→→→→→→→→→→→→        {W}{D}automated url finder{W}
{R}→→{W}-{R}→→→→→→→→→→→→→→→→→→→→→→          {C}{D}https://github.com/helviojunior/turbosearch{W}
{G}HHHHHH{W}           {R}→→→→→→{W}
{G}HHHHHH{W}           {R}→→→→{G}HH{W}  
{G}HHHHHH{W}           {R}→→{G}HHH{W}

    ''' % Configuration.version


    @staticmethod
    def mandatory():
        Color.pl('{!} {R}error: missing a mandatory option ({O}-t and -w{R}){G}, use -h help{W}\r\n')
        Configuration.exit_gracefully(0)

    @staticmethod
    def exit_gracefully(code=0):
        ''' Deletes temp and exist with the given code '''

        exit(code)


    @staticmethod
    def kill(code=0):
        ''' Deletes temp and exist with the given code '''

        os.kill(os.getpid(),signal.SIGTERM)


    @staticmethod
    def dump():
        ''' (Colorful) string representation of the configuration '''
        from .util.color import Color

        max_len = 20
        for key in Configuration.__dict__.keys():
            max_len = max(max_len, len(key))

        result  = Color.s('{W}%s  Value{W}\n' % 'Configuration Key'.ljust(max_len))
        result += Color.s('{W}%s------------------{W}\n' % ('-' * max_len))

        for (key,val) in sorted(Configuration.__dict__.items()):
            if key.startswith('__') or type(val) == staticmethod or val is None:
                continue
            result += Color.s("{G}%s {W} {C}%s{W}\n" % (key.ljust(max_len),val))
        return result

if __name__ == '__main__':
    Configuration.initialize(False)
    print(Configuration.dump())
