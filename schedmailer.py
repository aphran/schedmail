#!/usr/bin/env python
import json
import argparse
import logging
import sys
from datetime import datetime

def validdate(d):
    '''Validate a date (given as string) into a datetime object'''
    return datetime.strptime(d, '%Y-%m-%d') if d else datetime.today()

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
    parser.add_argument('-d', '--date',   dest='date', type=validdate, default=datetime.today(), help='default is today')
    parser.add_argument('-a', '--action', dest='action', default='show', choices=allactions, help='tells the program what to do')
    parser.add_argument('-b', '--body', help='contents of the appointed item (double quote it). Needed with actions "add" and "set"', default=None)
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
    logger.info('Processing action "{}" items for date: "{}"'.format(action, date))

def action_show():
    pass

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

if __name__ == '__main__':
    # globals - non parametrized
    schedfile = 'schedule.json'
    emails = [
        'afz902k@gmail.com'
    ]

    init()
    handle_action()
