#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .util.color import Color

import argparse, sys, os

class Arguments(object):
    ''' Holds arguments used by the Turbo Search '''
    restore = False

    def __init__(self, custom_args=''):
        self.verbose = any(['-v' in word for word in sys.argv])
        self.restore = any(['-R' in word for word in sys.argv])
        self.args = self.get_arguments(custom_args)

    def _verbose(self, msg):
        if self.verbose:
            return Color.s(msg)
        else:
            return argparse.SUPPRESS

    def get_arguments(self, custom_args=''):
        ''' Returns parser.args() containing all program arguments '''

        parser = argparse.ArgumentParser(usage=argparse.SUPPRESS,
                formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80, width=130))

        glob = parser.add_argument_group('General Setting')
        self._add_global_args(glob)

        custom_group = parser.add_argument_group('Custom Settings')
        self._add_custom_args(custom_group)

        wl_group = parser.add_argument_group('Word List Options')
        self._add_wl_args(wl_group)


        if self.restore and not custom_args == "":
            targs = custom_args.split()
            targs.pop(0) # remove o path do arquivo python, mantendo somente os parametros
            return parser.parse_args(targs)
        else:
            return parser.parse_args()


    def _add_global_args(self, glob):
        glob.add_argument('-t',
            action='store',
            dest='target',
            metavar='[target url]',
            type=str,
            help=Color.s('target url (ex: {G}http://10.10.10.10/path{W})'))

        glob.add_argument('-w',
            action='store',
            dest='word_list',
            metavar='[word list]',
            type=str,
            help=Color.s('word list to be tested'))

        glob.add_argument('-T',
            action='store',
            dest='tasks',
            default=16,
            metavar='[tasks]',
            type=int,
            help=Color.s('number of connects in parallel (per host, default: {G}16{W})'))


        glob.add_argument('-o',
            action='store',
            dest='out_file',
            metavar='[output file]',
            type=str,
            help=Color.s('save output to disk (default: {G}none{W})'))

        glob.add_argument('-x',
            action='store',
            dest='extensions',
            metavar='[extensions]',
            default='',
            type=str,
            help=Color.s('Append each request with this extensions (comma-separated values)'))


    def _add_custom_args(self, custom):
        custom.add_argument('-R',
            '--restore',
            action='store_true',
            default=False,
            dest='restore',
            help=Color.s('restore a previous aborted/crashed session'))

        custom.add_argument('-I',
            '--ignore',
            action='store_true',
            default=False,
            dest='ignore',
            help=Color.s('ignore an existing restore file (don\'t wait 10 seconds)'))

        custom.add_argument('-D',
            '--double-path',
            action='store_true',
            default=False,
            dest='doublepath',
            help=Color.s('multiply a payload set to search 2 path levels (ex: {G}word1/word2{W})'))

        custom.add_argument('--proxy',
            action='store',
            dest='proxy',
            metavar='[target proxy]',
            type=str,
            help=Color.s('target proxy URL (ex: {G}http://127.0.0.1:8080{W})'))

        custom.add_argument('--report-to',
            action='store',
            dest='report_to',
            metavar='[target proxy]',
            type=str,
            help=Color.s('target proxy URL to report only successful requests (ex: {G}http://127.0.0.1:8080{W})'))

        custom.add_argument('--deep',
            action='store_true',
            default=False,
            dest='deep',
            help=Color.s('Deep Search: Look for URLs inside of HTML results'))

        custom.add_argument('-v',
            '--verbose',
            action='count',
            default=0,
            dest='verbose',
            help=Color.s('Shows more options ({C}-h -v{W}). Prints commands and outputs. (default: {G}quiet{W})'))

        custom.add_argument('--full-log',
            action='store_true',
            dest='full_log',
            help=Color.s('Print full requested URLs (default: {G}no{W})'))

        custom.add_argument('--no-forward-location',
            action='store_true',
            dest='no_forward_location',
            help=Color.s('Disable forward to Location response address (default: {G}no{W})'))

        custom.add_argument('--ignore-result',
            action='store',
            dest='filter_rules',
            metavar='[filter]',
            default='',
            type=str,
            help=Color.s('ignore resuts by result code or/and size (ex1: 302 or ex2: 302:172 or ex3: 405,302:172 )'))

        custom.add_argument('--find',
            action='store',
            dest='find',
            metavar='[text to find]',
            default='',
            type=str,
            help=Color.s('Text to find in content or header (comma-separated values)'))

        custom.add_argument('--method',
            action='store',
            dest='request_method',
            metavar='[http method]',
            default='GET',
            type=str,
            help=Color.s('Specify request method (default: {G}GET{W}). Available methods: {G}GET{W}, {G}POST{W}, {G}PUT{W}, {G}PATCH{W}, {G}HEAD{W}, {G}OPTIONS{W}, {G}all{W} or comma-separated values'))

        custom.add_argument('--random-agent',
            action='store_true',
            default=False,
            dest='random_agent',
            help=Color.s('Use randomly selected HTTP User-Agent header value (default: {G}no{W})'))
        
        custom.add_argument('--header',
            action='store',
            dest='header',
            metavar='[headers]',
            default='',
            type=str,
            help=Color.s('JSON-formatted header key/value (ex: {G}\'{"PHPSESSID":"gvksi1cmjl2kqgntqof19sh823"}\'{W})'))

        custom.add_argument('--ci', '--case-insensitive',
            action='store_true',
            default=False,
            dest='case_insensitive',
            help=Color.s('Case Insensitive search: put all wordlist in lower case'))

        custom.add_argument('--stats-db',
            action='store_true',
            default=False,
            dest='statsdb',
            help=Color.s('Save reported URI at SQLite local database called stats.db (default: {G}no{W})'))
        
        custom.add_argument('--no-robots',
            action='store_true',
            default=False,
            dest='norobots',
            help=Color.s('Not look for robots.txt (default: {G}no{W})'))
        

    def _add_wl_args(self, custom):
        custom.add_argument('--md5-search',
            action='store_true',
            default=False,
            dest='md5_search',
            help=Color.s('Search for a MD5 Hash version of each word (default: {G}no{W})'))

        custom.add_argument('--sha1-search',
            action='store_true',
            default=False,
            dest='sha1_search',
            help=Color.s('Search for a SHA1 Hash version of each word (default: {G}no{W})'))

        custom.add_argument('--sha256-search',
            action='store_true',
            default=False,
            dest='sha256_search',
            help=Color.s('Search for a SHA256 Hash version of each word (default: {G}no{W})'))

        custom.add_argument('--hash-upper',
            action='store_true',
            default=False,
            dest='hash_upper',
            help=Color.s('In case of Hash Search be enabled, also search by Uppercase of Hash Hex Text (default: {G}no{W})'))

        custom.add_argument('--no-dupcheck',
            action='store_true',
            default=False,
            dest='nudupcheck',
            help=Color.s('Do not check duplicate words in wordlist. Use in case of big wordlists (default: {G}False{W})'))



'''
if __name__ == '__main__':
    from .util.color import Color
    from config import Configuration
    Configuration.initialize(False)
    a = Arguments(Configuration)
    args = a.args
    for (key,value) in sorted(args.__dict__.items()):
        Color.pl('{C}%s: {G}%s{W}' % (key.ljust(21),value))
'''