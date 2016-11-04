#!/usr/bin/env python3
import argparse, sys, time
from datetime import datetime

DATA_FILE = {'name': 'trep.dat', 'line_sep': '------\n',
        'rec_title': 'Action Records:', 'end_token': 'end' }


class Recorder:
    def __init__(self, datfile):
        self.datafile = datfile
        self.check_format()

    def get_file_contents(self):
        with open(self.datafile['name']) as f:
            lines = f.readlines()
        return lines

    def check_format(self):
        lines = self.get_file_contents()
        if len(lines) < 6:
            sys.exit('Bad header for data file %s' % self.datafile['name'])
        if lines[-1] != self.datafile['line_sep']:
            sys.exit('Last line of data file must be %s' % self.datafile['line_sep'])
        last_action = lines[-2].strip()
        if (last_action != self.datafile['rec_title']) and \
                (len(last_action.split(self.datafile['end_token'])) != 2):
            sys.exit('Last action must be "end"')

    def add_action(self, action, position=''):
        if action == 'finish':
            lines = self.get_file_contents()
            last_action = '%s %s %s\n' % (lines[-1].split(' ')[0],
                    self.datafile['end_token'], position)
            lines[-1] = last_action
            with open(self.datafile['name'], "w") as df:
                df.writelines(lines)
                df.write(self.datafile['line_sep'])
        else:
            with open(self.datafile['name'], "a") as df:
                df.write("%s %s %s\n" % (datetime.now().isoformat(), action, position))

    def start_recording(self):
        lines = self.get_file_contents()
        last_action = lines[-2].split(' ')
        last_finished_position = last_action[2].strip() if len(last_action) == 3 else 'None'
        print('Last finished position: %s' % last_finished_position)
        start_pos_input = input('Please input the start position[default: %s] '
                % last_finished_position)
        start_pos = float(last_finished_position) if start_pos_input == '' else \
                float(start_pos_input)
        self.add_action('start', start_pos)
        print('Start recording:')
        self.translating()

    def translating(self):
        PRINT_INV = 3
        try:
            while True:
                time.sleep(PRINT_INV)
                print('.', end='', flush=True)
        except KeyboardInterrupt:
            self.resume_recording()

    def resume_recording(self):
        self.add_action('pause')
        new_action = ''
        while new_action != 'r' and new_action != 'f':
            new_action = input('Resume or Finish[r/f]? ')
        if new_action == 'r':
            self.add_action('resume')
            self.translating()
        else:
            end_position = float(input('End position: '))
            self.add_action('finish', end_position)


class Calculator:
    def __init__(self, datfile):
        self.datafile = datfile

    def get_speed(self):
        pass

    def get_page_count(self):
        pass

    def get_total_pages(self):
        pass


class Reporter:
    def __init__(self, datfile):
        self.datafile = datfile

    def print_list(self):
        pass


    def print_report(self):
        pass


recorder = Recorder(DATA_FILE)
reporter = Reporter(DATA_FILE)

parser = argparse.ArgumentParser(description='Translation Reporter')
parser.add_argument('action', help='[r]ecord / [l]ist / [rep]ort')
args = parser.parse_args()

if args.action == 'r':
    recorder.start_recording()
elif args.action == 'l':
    reporter.print_list()
elif args.action == 'rep':
    reporter.print_report()
else:
    print('Bad command, list valid commands with "-h"')

