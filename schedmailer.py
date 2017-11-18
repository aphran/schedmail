#!/usr/bin/env python

import json
import argparse
from datetime import datetime

def validdate(d):
    return d if datetime.strptime(d, '%Y-%m-%d') else datetime.today()

schedfile = 'schedule.json'
emails = [
    'afz902k@gmail.com'
]

parser = argparse.ArgumentParser()

parser.add_argument('-d', '--date', type=validdate, default=datetime.today())

parser.parse_args()

print('Date is: {}'.format(args.date))

if False:
    for email in emails:
        #send email
        pass

