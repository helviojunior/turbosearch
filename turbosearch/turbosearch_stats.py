#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys, datetime, time, os
from urllib.parse import urlparse
import hashlib

from .util.color import Color
from .util.logger import Logger
from .util.process import Process
from .util.pathgetter import PathGetter
from .util.tools import Tools
from .util.database import Database
from .version import __version__


class Preparer:

    version = "0.0.0"
    db = None

    def __init__(self):
        pass

    def sha1Has(self, domain):
        hash_object = hashlib.sha1(domain.encode('UTF-8'))
        return hash_object.hexdigest()

    def prepare(self):
        self.db = Database(False, Configuration.stats_file)
        self.db.createDB()

        stats = self.db.selectStats()
        for uri in stats:
            rUri = urlparse(uri)
            hash = self.sha1Has(rUri.netloc)
            self.db.insertStatsL1(hash, rUri.path)
            
        self.db.clearStatsL2()

        paths = self.db.selectStatsL1()
        for path in paths:
            parts = path.strip("/").split("/")
            for p in parts:
                self.db.insertStatsL2(p.strip())

        lines = 0
        with open(Configuration.out_file, "a") as text_file:
            text_file.write("word,hits" + '\n')
            hits = self.db.selectStatsL2()
            for h in hits:
                text_file.write(h[0] + "," + str(h[1]) + '\n')
                lines+=1

        Logger.pl('{+} {O}%d{W} lines saved at {G}%s{W}' % (lines,Configuration.out_file))

        print(" ")

        pass


class Configuration(object):
    ''' Stores configuration variables and functions for Turbo Search. '''
    version = '0.0.9'

    stats_file = ''
    out_file = ''
    verbose =False
    cmd_line = ''

    @staticmethod
    def load_from_arguments():
        ''' Sets configuration values based on Argument.args object '''
        import getopt, argparse


        parser = argparse.ArgumentParser()

        requiredNamed = parser.add_argument_group('SETTINGS')

        requiredNamed.add_argument('-s',
            action='store',
            dest='stats_file',
            metavar='[stats.db path]',
            type=str,
            required=True,
            help=Color.s('Stats.db to be sumarized'))

        requiredNamed.add_argument('-o',
            action='store',
            dest='out_file',
            metavar='[output file]',
            type=str,
            help=Color.s('save output to disk in CSV format'))

        args = parser.parse_args()

        for a in sys.argv:
            Configuration.cmd_line += "%s " % a

        Configuration.stats_file = args.stats_file
        Configuration.out_file = args.out_file

        config_check = 0
        if Configuration.stats_file == '':
            config_check = 1

        if config_check == 1:
            Configuration.mandatory()


        Logger.pl('{+} {W}Startup parameters')


        if not os.path.isfile(Configuration.stats_file):
            Color.pl('{!} {R}error: Stats.db file not found {O}%s{R}{W}\r\n' % Configuration.word_list)
            Configuration.exit_gracefully(0)

        try:
            with open(Configuration.out_file, 'a') as f:
                # file opened for writing. write to it here
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
            db = Database(False, Configuration.stats_file)
            db.checkOpen()

        except IOError as x:
            if x.errno == errno.EACCES:
                Logger.pl('{!} {R}error: could not open output file {O}permission denied{R}{W}\r\n')
                sys.exit(0)
            elif x.errno == errno.EISDIR:
                Logger.pl('{!} {R}error: could not open output file {O}it is an directory{R}{W}\r\n')
                sys.exit(0)
            else:
                Logger.pl('{!} {R}error: could not open output file: {R}%s{W}\r\n' % str(x))
                sys.exit(0)


        Logger.pl('     {C}Stats.db file..:{O} %s{W}' % Configuration.stats_file)
        Logger.pl('     {C}Output file....:{O} %s{W}' % Configuration.out_file)


    @staticmethod
    def mandatory():
        Color.pl('{!} {R}error: missing a mandatory option ({O}-s and -o{R}){G}, use -h help{W}\r\n')
        sys.exit(0)

    @staticmethod
    def print_banner():
        """ Displays ASCII art of the highest caliber.  """
        
        version = str(__version__)

        Color.pl('''\

{G}HHHHHH{W}           {R}→→{G}HHH{W}
{G}HHHHHH{W}           {R}→→→→{G}HH{W}            
{G}HHHHHH{W}           {R}→→→→→→{W}
{R}→→{W}-{R}→→→→→→→→→→→→→→→→→→→→→→          {G}Turbo Search {D}v%s{W}{G} by Helvio Junior{W}
{R}→→{W}|{R}→→→→→→→→→→→→→→→→→→→→→→→→        {W}{D}automated url finder{W}
{R}→→{W}-{R}→→→→→→→→→→→→→→→→→→→→→→          {C}{D}https://github.com/helviojunior/turbosearch{W}
{G}HHHHHH{W}           {R}→→→→→→{W}
{G}HHHHHH{W}           {R}→→→→{G}HH{W}  
{G}HHHHHH{W}           {R}→→{G}HHH{W}

{O}
Script prepares stats.db with only statistics of the used words 

The stats will be output at CSV format with only word and hit count

If you want to contribute with top hits wordlist, please send the output CSV File
to helvio_junior [at] hotmial [dot] com
{W}

    ''' % version

    )


def run():
    Configuration.print_banner()

    d = Preparer()
    
    Configuration.load_from_arguments()

    try:

        d.prepare()

    except Exception as e:
        Color.pl('\n{!} {R}Error:{O} %s{W}' % str(e))

        if Configuration.verbose > 0 or True:
            Color.pl('\n{!} {O}Full stack trace below')
            from traceback import format_exc
            Color.p('\n{!}    ')
            err = format_exc().strip()
            err = err.replace('\n', '\n{W}{!} {W}   ')
            err = err.replace('  File', '{W}{D}File')
            err = err.replace('  Exception: ', '{R}Exception: {O}')
            Color.pl(err)

        Color.pl('\n{!} {R}Exiting{W}\n')

    except KeyboardInterrupt:
        Color.pl('\n{!} {O}interrupted, shutting down...{W}')

    sys.exit(0)

if __name__ == '__main__':
    run()