import argparse, sys, time, itertools, datetime as dt
from datetime import datetime
from operator import add, sub
from functools import reduce

import matplotlib.pyplot as plt
import numpy as np

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
        PRINT_INV = 60
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

    def conv_time(self, timestr):
        return datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%S.%f")

    def build_action(self, rec):
        lines = rec.split('\n')[:-1]
        action = {
            'start_time': self.conv_time(lines[0].split(' ')[0]),
            'start_page': float(lines[0].split(' ')[2]),
            'end_time': self.conv_time(lines[-1].split(' ')[0]),
            'end_page': float(lines[-1].split(' ')[2])
        }
        action['total_span'] = action['end_time'] - action['start_time']
        internals = [self.conv_time(line.split(' ')[0]) for line in lines[1:-1]]
        if len(internals) % 2 > 0:
            sys.exit('Numbers of pauses and resumes are not matched at page position %s' % action['start_page'])
        action['pauses'] = list(map(sub, internals[1::2], internals[::2]))
        action['translation_time'] = action['total_span'] \
                if len(action['pauses']) == 0 else \
                action['total_span'] - reduce(add, action['pauses'])
        action['pages'] = action['end_page'] - action['start_page']
        action['speed'] = action['pages'] * 3600 \
                / action['translation_time'].total_seconds()
        # use pages/hour as the speed unit instead of pages/second
        return action

    def get_report(self):
        records = open(self.datafile['name']).read().split(self.datafile['line_sep'])[1:-1]
        return list(map(self.build_action, records))


class Reporter:
    def __init__(self, datfile):
        self.datafile = datfile

    def getMonday(self, theday):
        delta = theday.isocalendar()[2] - 1
        monday = theday - dt.timedelta(days=delta)
        return '%s (%sth)' % (monday.strftime("%m-%d"), theday.isocalendar()[1])


    def add_display_tags(self, rec):
        rec['display_id'] = rec['start_time'].strftime("%m-%d %H:%M")
        rec['display_day'] = rec['start_time'].strftime("%m-%d")
        rec['display_week'] = self.getMonday(rec['start_time'])
        rec['display_month'] = rec['start_time'].strftime("%y.%m")
        return rec

    def build_records(self):
        cal = Calculator(self.datafile)
        return list(map(self.add_display_tags, cal.get_report()))

    def get_speed(self):
        speeds = [{'ID': rec['display_id'],
                   'Speed': round(rec['speed'], 2),
                   'Pages': round(rec['pages'], 1),
                   'time': round(rec['translation_time'].seconds / 60, 1)
                  } for rec in self.build_records()]
        return speeds

    def pages_group(self, key):
        page_per_day = [(rec[key], round(rec['pages']))
                for rec in self.build_records()]
        result = []
        for key, group in itertools.groupby(page_per_day, lambda x: x[0]):
            total_pages = reduce(add, [rec[1] for rec in group])
            result.append((key, total_pages))
        return result

    def finished_pages(self, key):
        pages = self.pages_group(key)
        finished = 0
        fp = []
        for p in pages:
            finished = finished + p[1]
            fp.append((p[0], finished))
        return fp

    def print_list(self):
        print('=== Speed Report ===')
        for rec in self.get_speed():
            print('%s: ' % rec['ID'], end='', flush=True)
            print('%s %s, ' % (rec['Pages'], 'pages'), end='', flush=True)
            print('%s %s, ' % (rec['time'], 'minutes'), end='', flush=True)
            print('%s %s' % (rec['Speed'], 'pages/hr'), end='', flush=True)
            print()
        print('=== Pages by Day ===')
        print(self.pages_group('display_day'))
        print('=== Finished Pages by Day ===')
        print(self.finished_pages('display_day'))
        print('=== Pages by Week ===')
        print(self.pages_group('display_week'))
        print('=== Finished Pages by Week ===')
        print(self.finished_pages('display_week'))
        print('=== Pages by Month ===')
        print(self.pages_group('display_month'))
        print('=== Finished Pages by Month ===')
        print(self.finished_pages('display_month'))

    def get_total_pages(self):
        return int(open(self.datafile['name']).readlines()[1].split(': ')[1].strip())

    def print_report(self):
        fig = plt.figure(1)
        fig.canvas.set_window_title('Trep Report')

        # speed report
        plt.subplot(421)
        plt.ylabel('speed (pages/hr)')
        speeds_and_pages = self.get_speed()
        xs = range(0, len(speeds_and_pages))
        speeds = [x['Speed'] for x in speeds_and_pages]
        plt.ylim(0, max(speeds) + 1)
        plt.tick_params(bottom='off', labelbottom='off')
        plt.plot(xs, speeds, color='blue', linewidth=2.5, marker='o')

        plt.subplot(423)
        plt.ylabel('pages per action')
        pages = [x['Pages'] for x in speeds_and_pages]
        plt.xlabel('Action Time')
        plt.ylim(0, max(pages) + 1)
        plt.xticks(xs, [x['ID'] for x in speeds_and_pages], rotation=30)
        plt.plot(xs, pages, color='red', linewidth=2.5, marker='o')

        plt.subplot(422)
        plt.ylabel('pages per day')
        pages_per_day = self.pages_group('display_day')
        xs = range(0, len(pages_per_day))
        pages = [p[1] for p in pages_per_day]
        plt.ylim(0, max(pages) + 1)
        plt.tick_params(bottom='off', labelbottom='off')
        plt.plot(xs, pages, color='blue', linewidth=2.5, marker='o')

        plt.subplot(424)
        plt.ylabel('total pages per day')
        total_pages_per_day = self.finished_pages('display_day')
        pages = [p[1] for p in total_pages_per_day]
        plt.xlabel('Day')
        plt.ylim(0, self.get_total_pages())
        plt.xticks(xs, [p[0] for p in pages_per_day], rotation=0)
        plt.plot(xs, pages, color='red', linewidth=2.5, marker='o')

        plt.subplot(425)
        plt.ylabel('pages per week')
        pages_per_week = self.pages_group('display_week')
        xs = range(0, len(pages_per_week))
        pages = [p[1] for p in pages_per_week]
        plt.ylim(0, max(pages) + 1)
        plt.tick_params(bottom='off', labelbottom='off')
        plt.plot(xs, pages, color='blue', linewidth=2.5, marker='o')

        plt.subplot(427)
        plt.ylabel('total pages per week')
        total_pages_per_week = self.finished_pages('display_week')
        pages = [p[1] for p in total_pages_per_week]
        plt.xlabel('Week')
        plt.ylim(0, self.get_total_pages())
        plt.xticks(xs, [p[0] for p in pages_per_week], rotation=0)
        plt.plot(xs, pages, color='red', linewidth=2.5, marker='o')

        plt.subplot(426)
        plt.ylabel('pages per month')
        pages_per_month = self.pages_group('display_month')
        xs = range(0, len(pages_per_month))
        pages = [p[1] for p in pages_per_month]
        plt.ylim(0, max(pages) + 1)
        plt.tick_params(bottom='off', labelbottom='off')
        plt.plot(xs, pages, color='blue', linewidth=2.5, marker='^')

        plt.subplot(428)
        plt.ylabel('total pages per month')
        total_pages_per_month = self.finished_pages('display_month')
        pages = [p[1] for p in total_pages_per_month]
        plt.xlabel('Month')
        plt.ylim(0, self.get_total_pages())
        plt.xticks(xs, [p[0] for p in pages_per_month], rotation=0)
        plt.plot(xs, pages, color='red', linewidth=2.5, marker='o')

        plt.show()


recorder = Recorder(DATA_FILE)
reporter = Reporter(DATA_FILE)

parser = argparse.ArgumentParser(description='Translation Reporter')
parser.add_argument('action', help='[s]tart / [l]ist / [r]eport')
args = parser.parse_args()

if args.action == 's':
    recorder.start_recording()
elif args.action == 'l':
    reporter.print_list()
elif args.action == 'r':
    reporter.print_report()
else:
    print('Bad command, list valid commands with "-h"')

