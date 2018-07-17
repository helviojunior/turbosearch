#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os, subprocess, socket, re, requests, errno

from .args import Arguments
from .util.color import Color
from .util.logger import Logger

class Configuration(object):
    ''' Stores configuration variables and functions for Turbo Search. '''
    version = '0.0.1'

    initialized = False # Flag indicating config has been initialized
    verbose = 0
    target = ''
    word_list = ''
    out_file = ''
    extensions = []

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

        args = Arguments(Configuration).args

        Color.pl('{+} {W}Startup parameters')

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

        if not os.path.isfile(Configuration.word_list):
            Color.pl('{!} {R}error: word list file not found {O}%s{R}{W}\r\n' % Configuration.word_list)
            Configuration.exit_gracefully(0)

        if Configuration.out_file != '':
            try:
                with open(Configuration.out_file, 'w') as f:
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

        Logger.pl('     {C}tasks:{O} %s{W}' % Configuration.tasks)

        if args.verbose:
            Logger.pl('     {C}option:{O} verbosity level %d{W}' % Configuration.verbose)

        Logger.pl('     {C}word list:{O} %s{W}' % Configuration.word_list)

        if args.forward_location:
            Configuration.forward_location = True
            Logger.pl('     {C}forward location redirects:{O} yes{W}')

        if args.extensions != '':
            ext_list = args.extensions.split(",")
            for ex in ext_list:
                if ex.strip() != '':
                    Configuration.extensions.append(ex.strip())

        if len(Configuration.extensions) > 0:
            ext_txt = ''
            for ex in Configuration.extensions:
                ext_txt += '(%s)' % ex

        Logger.pl('     {C}extension list:{O} %s{W}' % ext_txt)


    @staticmethod
    def get_banner():
            """ Displays ASCII art of the highest caliber.  """
            return '''\

{G}HHHHHH{W}           {R}→→{G}HHH{W}
{G}HHHHHH{W}           {R}→→→→{G}HH{W}            
{G}HHHHHH{W}           {R}→→→→→→{W}
{R}→→{W}-{R}→→→→→→→→→→→→→→→→→→→→→→          {G}Turbo Search {D}v%s{W}{G} by Helvio Junior{W}
{R}→→{W}|{R}→→→→→→→→→→→→→→→→→→→→→→→→        {W}{D}automated url finder{W}
{R}→→{W}-{R}→→→→→→→→→→→→→→→→→→→→→→          {C}{D}https://gitlab.com/helvio_junior/overflow{W}
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