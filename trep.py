#!/usr/bin/env python3
import argparse, sys, time
from datetime import datetime

DATAFILE = 'trep.dat'
LINE_SEP = '------\n'
REC_TITLE = 'Action Records:'
END_TOKEN = 'end'


def get_file_contents(inputfile):
    # lines[-1] is an empty string, not the real last line
    #return open(inputfile).read().split('\n')[:-1]
    with open(inputfile) as f:
        lines = f.readlines()
    return lines

def check_format(inputfile):
    lines = get_file_contents(inputfile)
    if len(lines) < 6:
        sys.exit('Bad header for data file %s' % inputfile)
    if lines[-1] != LINE_SEP:
        sys.exit('Last line of data file must be %s' % LINE_SEP)
    last_action = lines[-2].strip()
    if (last_action != REC_TITLE) and \
            (len(last_action.split(END_TOKEN)) != 2):
        sys.exit('Last action must be "end"')


def add_action(inputfile, action, position=''):
    if action == 'finish':
        lines = get_file_contents(inputfile)
        last_action = '%s %s %s\n' % (lines[-1].split(' ')[0], END_TOKEN, position)
        lines[-1] = last_action
        with open(inputfile, "w") as df:
            df.writelines(lines)
            df.write(LINE_SEP)
    else:
        with open(inputfile, "a") as df:
            df.write("%s %s %s\n" % (datetime.now().isoformat(), action, position))

def start_recording(inputfile):
    lines = get_file_contents(inputfile)
    last_action = lines[-2].split(' ')
    last_finished_position = last_action[2].strip() if len(last_action) == 3 else 'None'
    print('Last finished position: %s' % last_finished_position)
    start_pos_input = input('Please input the start position[default: %s] '
            % last_finished_position)
    start_pos = float(last_finished_position) if start_pos_input == '' else \
            float(start_pos_input)
    add_action(inputfile, 'start', start_pos)
    print('Start recording:')
    translating(inputfile)


def translating(inputfile):
    PRINT_INV = 3
    try:
        while True:
            time.sleep(PRINT_INV)
            print('.', end='', flush=True)
    except KeyboardInterrupt:
        resume_recording(inputfile)


def resume_recording(inputfile):
    add_action(inputfile, 'pause')
    new_action = ''
    while new_action != 'r' and new_action != 'f':
        new_action = input('Resume or Finish[r/f]? ')
    if new_action == 'r':
        add_action(inputfile, 'resume')
        translating(inputfile)
    else:
        end_position = float(input('End position: '))
        add_action(inputfile, 'finish', end_position)


def print_list(inputfile):
    pass


def draw_report(inputfile):
    pass


check_format(DATAFILE)

parser = argparse.ArgumentParser(
    description='Translation Reporter')
parser.add_argument('action',
                    help='rec/list/report')
args = parser.parse_args()

if args.action == 'rec':
    start_recording(DATAFILE)
elif args.action == 'list':
    print_list(DATAFILE)
elif args.action == 'report':
    draw_report(DATAFILE)
else:
    print('Bad command, list valid commands with "-h"')

