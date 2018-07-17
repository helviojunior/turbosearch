#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .util.color import Color

import argparse, sys, os

class Arguments(object):
    ''' Holds arguments used by the Turbo Search '''

    def __init__(self, configuration):
        self.verbose = any(['-v' in word for word in sys.argv])
        self.config = configuration
        self.args = self.get_arguments()

    def _verbose(self, msg):
        if self.verbose:
            return Color.s(msg)
        else:
            return argparse.SUPPRESS

    def get_arguments(self):
        ''' Returns parser.args() containing all program arguments '''

        parser = argparse.ArgumentParser(usage=argparse.SUPPRESS,
                formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80, width=130))

        glob = parser.add_argument_group('SETTINGS')
        self._add_global_args(glob)

        custom_group = parser.add_argument_group('CUSTOM')
        self._add_custom_args(custom_group)

        return parser.parse_args()


    def _add_global_args(self, glob):
        glob.add_argument('-v',
            '--verbose',
            action='count',
            default=0,
            dest='verbose',
            help=Color.s('Shows more options ({C}-h -v{W}). Prints commands and outputs. (default: {G}quiet{W})'))

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


    def _add_custom_args(self, custom):
        custom.add_argument('--forward-location',
            action='store_true',
            dest='forward_location',
            help=Color.s('Forward to Location response address (default: {G}yes{W})'))

        custom.add_argument('-x',
            action='store',
            dest='extensions',
            metavar='[extensions]',
            default='',
            type=str,
            help=Color.s('Append each request with this extensions (comma-separated values)'))


if __name__ == '__main__':
    from .util.color import Color
    from config import Configuration
    Configuration.initialize(False)
    a = Arguments(Configuration)
    args = a.args
    for (key,value) in sorted(args.__dict__.items()):
        Color.pl('{C}%s: {G}%s{W}' % (key.ljust(21),value))
