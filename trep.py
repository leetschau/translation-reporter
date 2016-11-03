#!/usr/bin/env python
import argparse

parser = argparse.ArgumentParser(
    description='Translation Reporter')
parser.add_argument('action',
                    help='rec/list/report')
args = parser.parse_args()

print(args.action)
