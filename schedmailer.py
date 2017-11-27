#!/usr/bin/env python
import json
import argparse
import logging
import sys
from datetime import date
from datetime import time
from datetime import datetime
import pprint
import pyowm

class CalDB(argparse.Namespace):

    def default_day_record(self, msg = '', wth = {}):
        return {
            'msg': msg,
            'wth': wth
        }

    def default_location_record(self, day, msg = '', wth = {}):
        return { day: self.default_day_record(msg, wth) }

    def default_db_record(self, location, day, msg = '', wth = {}):
        return { location: self.default_location_record(day, msg, wth) }

    # DB methods

    def __init__(self, json_in = None, dbfile = None):
        if json_in:
            self.set_from_json(json_in)
        else:
            self.data = {}
            if dbfile:
                self.dbfile = dbfile
                self.init_db(dbfile)

    def init_db(self, pfile = None):
        if not pfile:
            pfile = self.dbfile
        if pfile:
            self.set_from_json(self.read_file(pfile))

    def default_update(self, location, day, msg = '', wth = {}):
        self.data.update(self.default_db_record(location, day, msg, wth))

    def write_db(self):
        self.write_file(self.dbfile, self.get_json())

    def get_json(self):
        return json.dumps(self.data)

    def set_from_json(self, json_in):
        try:
            self.data = json.loads(json_in)
        except ValueError:
            logger.warn('Could not load JSON data from file, defaulting to empty dict')
            self.data = {}

    def read_file(self, jfile):
        with open(jfile, 'a+') as jf:
            rdata = jf.read()
        return rdata

    def write_file(self, jfile, sdata):
        with open(jfile, 'w+') as jf:
            jf.write(sdata)

    # Location methods

    def del_location(self, loc_name):
        self.data[loc_name] = None

    def upd_location(self, loc_name, loc_dict = {}, loc_json_in = None):
        if loc_json_in:
            self.data[loc_name] = json.loads(loc_json_in)
        else:
            self.data[loc_name] = loc_dict

    def get_loc_json(self, loc_name):
        return json.dumps(self.data[loc_name])

    def get_location(self, loc_name):
        try:
            return self.data[loc_name]
        except KeyError as e:
            return {}

    # Date methods

    def del_date(self, loc_name, pdate):
        self.data[loc_name][pdate] = None

    def upd_date(self, loc_name, pdate, date_dict = {}, date_json_in = None):
        if date_json_in:
            self.data[loc_name][pdate] = json.loads(date_json_in)
        else:
            self.data[loc_name][pdate] = date_dict

    def get_date_json(self, loc_name, pdate):
        try:
            date_record = json.dumps(self.data[loc_name][pdate])
        except KeyError as e:
            logger.warn('No records found for location {} and date {}, returning empty string'.format(loc_name, pdate))
            date_record = ''
        return date_record

    def get_date(self, loc_name, pdate):
        try:
            return self.data[loc_name][pdate]
        except KeyError as e:
            return self.default_day_record

    # Sub-date methods

    def get_msg(self, loc_name, pdate):
        return self.data[loc_name][pdate]['msg']

    def del_msg(self, loc_name, pdate):
        self.data[loc_name][pdate]['msg'] = None

    def upd_msg(self, loc_name, pdate, msg):
        self.data[loc_name][pdate]['msg'] = msg

    def append_msg(self, loc_name, pdate, msg):
        self.data[loc_name][pdate]['msg'] += msg

    def get_weather(self, loc_name, pdate):
        try:
            return self.data[loc_name][pdate]['wth']
        except KeyError as e:
            logger.warn('Weather record for {}, {} did not exist, returned empty dict'.format(loc_name, pdate))
            return {}

    def del_weather(self, loc_name, pdate):
        try:
            self.data[loc_name][pdate]['wth'] = None
        except KeyError as e:
            logger.info('Weather record for {}, {} did not exist, no action taken'.format(loc_name, pdate))

    def upd_weather(self, loc_name, pdate, pweather):
        try:
            self.data[loc_name][pdate]['wth'] = pweather
        except KeyError as e:
            logger.info('No records found for location {} and date {}, initializing!'.format(loc_name, pdate))
            self.default_update(loc_name, pdate, wth = pweather)

def valid_date(d):
    '''Validate a date (given as string) into a datetime object'''
    return datetime.strptime('{} 00:00'.format(d), '%Y-%m-%d %h:%m') if d else datetime.combine(date.today(), time.min)

def valid_out(opt):
    outs = ''
    if not opt:
        return default_outs
    else:
        for item in opt:
            if item in all_outs:
                outs += item
            else:
                raise ValueError('Invalid output "{}"'.format(item))
        return outs

def setup_logger():
    '''Initialize logging'''
    global logger; logger = logging.getLogger(sys.argv[0])
    loghandler = logging.StreamHandler()
    loghandler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(loghandler)
    logger.setLevel(logging.INFO)

def get_default_place():
    return default_place

def handle_args():
    '''Parse incoming arguments and update globals accordingly'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date',   dest='tdate', type=valid_date, default=valid_date(None), help='default is today')
    parser.add_argument('-a', '--action', dest='action', default=default_action, choices=all_actions, help='tells the program what to do')
    parser.add_argument('-b', '--body', help='contents of the appointed item (double quote it). Needed with action "write"', default=None)
    parser.add_argument('-p', '--place', dest='place', default=get_default_place(), help='weather location, formatted as "City,CC" where CC is the country code')
    parser.add_argument('-o', '--out', dest='outs', type=valid_out, default=valid_out(None), help='desired outputs, allowed options are "e" for email and "s" for standard output. Specify them as a single word. Example: "-o es" # sets output to be both email and standard output')
    globals().update(parser.parse_args().__dict__)

def init():
    init_globals()
    setup_logger()
    handle_args()
    init_db()

def init_db():
    global dbobj
    dbobj = CalDB(dbfile = sched_file)
    logger.info('DB Initialized with data: {}'.format(dbobj.get_json()))

def init_globals():
    global template_file
    template_file = 'mail_template.jj'
    global sched_file
    sched_file = 'dbschedule.json'
    global emails
    emails = [
        'afz902k@gmail.com'
    ]
    global default_place
    default_place = 'Aguascalientes,MX'
    global all_actions
    all_actions = ['render', 'write', 'del']
    global default_action
    default_action = 'render'
    global all_outs
    all_outs = 'es'
    global default_outs
    default_outs = 's'

def get_date_str():
    return tdate.strftime('%Y-%m-%d')

def out_email(contents):
    logger.info('Sending e-mail!')

def out_cli(contents):
    msg = '\n' + contents if contents else 'No records for this day'
    logger.info('Information for location: {} and date: {} - {}'.format(place, get_date_str(), msg))

def action_render():
    init_weather()
    logger.info('Before:\n{}'.format(dbobj.get_json()))
    dbobj.upd_weather(place, get_date_str(), get_weather_for_location(place))
    logger.info('Afer:\n{}'.format(dbobj.get_json()))
    dbobj.write_db()
    record = dbobj.get_date(place, get_date_str()) #this is a dict
    if body:
        logger.info('Specified body will be appended to message')
        record['msg'] += body
    contents = clean_dump(record)
    if 'e' in outs:
        for email in emails:
            out_email(contents)
    if 's' in outs:
            out_cli(contents)

def action_write():
    if not body:
        logger.error('Please specify a body (-b or --body) when using action "{}"'.format(action))
        raise ValueError('Missing argument "body"')

def action_del():
    # validate args
    if body:
        logger.warn('Ignoring body (-b or --body) when using action "{}"'.format(action))

def handle_action():
    if action not in all_actions:
        logger.error('Action "{}" is invalid. How did this EVEN?! (valid actions are: {})'.format(action, all_actions))
        raise ValueError('Invalid action')
    try:
        action_method = 'action_{}()'.format(action)
        eval(action_method)
    except:
        raise
    #except NameError as e:
    #    logger.error('Action method "{}" not implemented'.format(action_method))
    #    raise NotImplementedError
    logger.info('Processing action "{}" items for date: "{}"'.format(action, tdate))

def init_weather():
    global weathers
    global apikey
    global owm
    weathers = {}
    apikey = 'ee0c5718cfe312ec4f8f0acfb7542591'
    try:
        owm = pyowm.OWM(apikey)
    except Exception as e:
        logger.error(e)
        raise e

def get_weather_for_location(lplace):
    if not lplace: lplace = place
    logger.debug('Getting weather data for "{}" today ({})'.format(lplace, tdate))
    wth = owm.weather_at_place(lplace).get_weather()
    message_dict = {
        'Weather data for {}'.format(lplace): {
            'Status' : wth.get_detailed_status(),
            'Temperature': wth.get_temperature(),
            'Humidity': wth.get_humidity(),
            'Wind': wth.get_wind()
        }
    }
    return message_dict

def compose_msg(extra_msg = ''):
    template = ''
    #db_weather, db_msg = read_db(date)
    #template = render_template(db_weather, db_msg, extra_msg)
    return template

def clean_dump(obj, depth = 0):
    def appendln(a, b):
        if not b.endswith('\n'): b += '\n'
        ret_str = '{}{}'.format(a, b)
        return ret_str

    pad = '  ' * depth
    dumped = ''
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                dumped = appendln(dumped, '{}{}:'.format(pad, k))
                dumped = appendln(dumped, clean_dump(v, depth + 1))
            else:
                dumped = appendln(dumped, '{}{}: {}'.format(pad, k, v))
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumped = appendln(dumped, clean_dump(v))
            else:
                dumped = appendln(dumped, v)
    else:
        dumped = appendln(dumped, obj)
    return dumped

if __name__ == '__main__':
    init()
    handle_action()
