import argparse, sys, time, itertools, datetime as dt
from datetime import datetime
from operator import add, sub
from functools import reduce

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
        action['speed'] = action['pages'] * 3600 * 24 \
                / action['translation_time'].total_seconds()
        # use pages/day as the speed unit instead of pages/second
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
        speeds = [{'ID': rec['display_id'], 'Speed': round(rec['speed'], 2),
            'Pages': round(rec['pages'])} for rec in self.build_records()]
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
            print('%s %s' % (rec['Speed'], 'pages/d'), end='', flush=True)
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

    def print_report(self):
        pass


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

