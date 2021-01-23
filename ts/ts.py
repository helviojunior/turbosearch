#!/usr/bin/python3
# -*- coding: UTF-8 -*-

try:
    from .config import Configuration
except (ValueError, ImportError) as e:
    raise Exception('You may need to run TurboSearch from the root directory (which includes README.md)', e)


import sys, datetime, time, os, requests
from .util.color import Color
from .util.logger import Logger
from .util.process import Process
from .util.pathgetter import PathGetter
from .util.tools import Tools
from .util.getter import Getter, DirectoryInfo

class TurboSearch(object):

    def main(self):
        ''' Either performs action based on arguments, or starts attack scanning '''

        #if os.getuid() != 0:
        #    Color.pl('{!} {R}error: {O}TurboSearch{R} must be run as {O}root{W}')
        #    Color.pl('{!} {O}re-run as: sudo ./turbosearch.py{W}')
        #    Configuration.exit_gracefully(0)

        self.dependency_check()

        Configuration.initialize()

        self.run()

    def dependency_check(self):
        ''' Check that required programs are installed '''
        required_apps = ['ip', 'awk', 'cut']
        optional_apps = []
        missing_required = False
        missing_optional = False

        for app in required_apps:
            if not Process.exists(app):
                missing_required = True
                Color.pl('{!} {R}error: required app {O}%s{R} was not found' % app)

        for app in optional_apps:
            if not Process.exists(app):
                missing_optional = True
                Color.pl('{!} {O}warning: recommended app {R}%s{O} was not found' % app)

        if missing_required:
            Color.pl('{!} {R}required app(s) were not found, exiting.{W}')
            sys.exit(-1)

        if missing_optional:
            Color.pl('{!} {O}recommended app(s) were not found')
            Color.pl('{!} {O}TurboSearch may not work as expected{W}')

    def run(self):
        '''
            Main program.
            1) Scans for targets, asks user to select targets
            2) Attacks each target
        '''


        try:
            get = PathGetter()
            get.load_wordlist()

            now = time.time()
            ts = int(now)
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            Logger.pl('     {C}start time {O}%s{W}' % timestamp)
            if get.duplicated > 0:
                Logger.pl('     {C}duplicate {O}%d{C} words, duplicates ignored {O}%d{C} words{W}' % (get.len(), get.duplicated))
            else:
                Logger.pl('     {C}duplicate {O}%d{C} words{W}' % get.len())
            Logger.pl(' ')

            try:
                proxy={}
                if Configuration.proxy != '':
                    proxy = {
                      'http': Configuration.proxy,
                      'https': Configuration.proxy,
                    }

                headers = Configuration.user_headers
                if Configuration.user_agent:
                    headers['User-Agent'] = Configuration.user_agent
                    

                
                requests.packages.urllib3.disable_warnings()
                r = requests.get(Configuration.target, verify=False, timeout=10, headers=headers, proxies=proxy)

                Logger.pl('{+} {W}Connection test againt {C}%s{W} OK! (CODE:%d|SIZE:%d) ' % (Configuration.target, r.status_code, len(r.text)))

                Tools.check_content(r);

            except Exception as e:
                Logger.pl('{+} {R}connectivity check error: {O}%s{W}' % e)
                Configuration.exit_gracefully(1)

            if Configuration.proxy_report_to != '':
                try:
                    proxy={}

                    proxy = {
                      'http': Configuration.proxy_report_to,
                      'https': Configuration.proxy_report_to,
                    }
                    
                    headers = Configuration.user_headers
                    if Configuration.user_agent:
                        headers['User-Agent'] = Configuration.user_agent
                        

                    requests.packages.urllib3.disable_warnings()
                    r = requests.get(Configuration.target, verify=False, timeout=10, headers=headers, proxies=proxy)

                    Logger.pl('{+} {W}Connection test againt using report to proxy {C}%s{W} OK! (CODE:%d|SIZE:%d) ' % (Configuration.target, r.status_code, len(r.text)))

                except Exception as e:
                    Logger.pl('{+} {R}connectivity check error using report to proxy: {O}%s{W}' % e)
                    Configuration.exit_gracefully(1)

            Logger.pl('     ')

            Logger.pl('{+} {W}Scanning url {C}%s{W} ' % Configuration.target)

            get.added = Configuration.restored_paths
            get.current_uri = Configuration.restored_uri
            Getter.deep_links = Configuration.restored_deep_links
            
            get.run()
            Logger.pl('     ')

            
            if os.path.exists("turbosearch.restore"): 
                os.remove("turbosearch.restore")

        except Exception as e:
            Color.pl("\n{!} {R}Error: {O}%s" % str(e))
            if Configuration.verbose > 0 or True:
                Color.pl('\n{!} {O}Full stack trace below')
                from traceback import format_exc
                Color.p('\n{!}    ')
                err = format_exc().strip()
                err = err.replace('\n', '\n{W}{!} {W}   ')
                err = err.replace('  File', '{W}{D}File')
                err = err.replace('  Exception: ', '{R}Exception: {O}')
                Color.pl(err)
        except KeyboardInterrupt:
            Color.pl('\n{!} {O}interrupted{W}\n')


        now = time.time()
        ts = int(now)
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        Logger.pl('{+} {C}End time {O}%s{W}' % timestamp)


        Logger.pl("{+} Finished tests against {C}%s{W}, exiting" % Configuration.target)


        #Configuration.delete_temp()

    def print_banner(self):
        """ Displays ASCII art of the highest caliber.  """
        Color.pl(Configuration.get_banner())

    def user_wants_to_continue(self, targets_remaining, attacks_remaining=0):
        ''' Asks user if attacks should continue onto other targets '''
        if attacks_remaining == 0 and targets_remaining == 0:
            # No targets or attacksleft, drop out
            return

        prompt_list = []
        if attacks_remaining > 0:
            prompt_list.append(Color.s('{C}%d{W} attack(s)' % attacks_remaining))
        if targets_remaining > 0:
            prompt_list.append(Color.s('{C}%d{W} target(s)' % targets_remaining))
        prompt = ' and '.join(prompt_list)
        Color.pl('{+} %s remain, do you want to continue?' % prompt)

        prompt = Color.s('{+} type {G}c{W} to {G}continue{W}' +
                         ' or {R}s{W} to {R}stop{W}: ')

        if raw_input(prompt).lower().startswith('s'):
            return False
        else:
            return True


def run():
    o = TurboSearch()
    o.print_banner()

    try:
        o.main()

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

    Configuration.exit_gracefully(0)

if __name__ == '__main__':
    run()