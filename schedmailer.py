#!/usr/bin/env python
import json
import argparse
import logging
import sys
from datetime import date
from datetime import time
from datetime import datetime

def validdate(d):
    '''Validate a date (given as string) into a datetime object'''
    return datetime.strptime("{} 00:00".format(d), '%Y-%m-%d %h:%m') if d else datetime.combine(date.today(), time.min)

def setup_logger():
    '''Initialize logging'''
    global logger; logger = logging.getLogger(sys.argv[0])
    loghandler = logging.StreamHandler()
    loghandler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(loghandler)
    logger.setLevel(logging.INFO)

def handle_args():
    '''Parse incoming arguments and update globals accordingly'''
    global allactions; allactions = ['show', 'send', 'add', 'del', 'set']
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date',   dest='tdate', type=validdate, default=validdate(None), help='default is today')
    parser.add_argument('-a', '--action', dest='action', default='show', choices=allactions, help='tells the program what to do')
    parser.add_argument('-b', '--body', help='contents of the appointed item (double quote it). Needed with actions "add" and "set"', default=None)
    parser.add_argument('-p', '--places', dest='places', type=list, default=['Aguascalientes,MX'], help='weather location, formatted as "City,CC" where CC is the country code')
    globals().update(parser.parse_args().__dict__)
    # validate args
    if (action == 'show' or action == 'del') and body:
        logger.warn('Ignoring body (-b or --body) when using action "{}"'.format(action))
    if (action == 'add'  or action == 'set') and not body:
        logger.error('Please specify a body (-b or --body) when using action "{}"'.format(action))
        raise ValueError('Missing argument "body"')

def init():
    setup_logger()
    handle_args()

def handle_action():
    if action not in allactions:
        logger.error('Action "{}" is invalid. How did this EVEN?! (valid actions are: {})'.format(action, allactions))
        raise ValueError('Invalid action')
    try:
        eval('action_{}()'.format(action))
    except NameError as e:
        logger.error('Action "{}" not implemented'.format(action))
        raise NotImplementedError
    logger.info('Processing action "{}" items for date: "{}"'.format(action, tdate))

def action_show():
    init_weather()
    get_weather()

def action_send():
    if body: logger.info('Specified body will be appended to message')
    #for email in emails:
        #send email

def action_add():
    pass

def action_set():
    pass

def action_del():
    pass

def get_eod():
    return datetime.combine(tdate.date(), time.max)

def init_weather():
    global apikey
    apikey = 'tbd'
    try:
        pass # instantiate weather object with API key
    except Exception as e:
        logger.error(e)
        raise e

def get_weather(lplaces = []):
    tdate_eod = get_eod()
    if not lplaces: lplaces = places
    for where in lplaces:
        logger.info('Getting weather data for "{}" from {} to {}'.format(where, tdate, tdate_eod))
        # use already instantiated weather object to query location and time range

if __name__ == '__main__':
    # globals - non parametrized
    schedfile = 'schedule.json'
    emails = [
        'afz902k@gmail.com'
    ]

    init()
    handle_action()
