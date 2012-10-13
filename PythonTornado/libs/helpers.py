#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=

""" Helper functions

Consists of functions to typically be used within templates

.. moduleauthor:: <>

"""

import collections
import random
import logging
import re
import pytz
from datetime import datetime, timedelta, tzinfo
import calendar
import cPickle
import zlib
import json
from dateutil import parser
import time

import sys
sys.setrecursionlimit(4000)

from HTMLParser import HTMLParser#, HTMLParseError


class MLStripper(HTMLParser):
  """ HTML tag remover

  """
  def __init__(self):
    """ n/a

    """
    self.reset()
    self.fed = []

  def handle_data(self, d):
    """  n/a

    """
    self.fed.append(d)

  def get_data(self):
    """ n/a

    """
    return ''.join(self.fed)

def strip_tags(html):
  """ Remove any html tags

  Args:
    * `html` (str): html string

  Returns:
    ``str``.
  """
  stripped = ''
  #s = MLStripper()
  #try:
  #  s.feed(html)
  #  stripped = s.get_data()
  #except HTMLParseError:
  #  stripped = re.sub(r'<[^>]*?>', '', html)
  stripped = re.sub(r'<[^>]*?>', '', html)

  return stripped

email_re = re.compile(
# dot-atom
r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
# quoted-string
r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'
# domain
r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', 
re.IGNORECASE
)


#PICKLE_MAX_RECURSION_DEPTH = 4000

def zdumps(obj):
  """ Helpers to serialize and compress objects

  Args:
    * `obj` (object): object to compress and serialize

  Returns:
    ``str``. 

  """
  #sys.setrecursionlimit(PICKLE_MAX_RECURSION_DEPTH)
  return zlib.compress(cPickle.dumps(obj, cPickle.HIGHEST_PROTOCOL))

def bin_zdumps(obj):
  """ Helper to serialize and compress objects and 
  convert to mongo Binary format safe for insert

  Args:
    * `obj` (object): object to compress and serialize

  Returns:
    ``Binary``. 

  """
  return Binary(zdumps(obj))

def zloads(zstr):
  """ Helper to uncompress and deserialize an object

  Args:
    * `zstr` (str): compressed and serialized object

  Returns:
    ``object``. 
  """
  #sys.setrecursionlimit(PICKLE_MAX_RECURSION_DEPTH)
  return cPickle.loads(zlib.decompress(zstr))

def jzdumps(obj):
  """ Helpers to serialize and compress objects
  using json and zlib

  Args:
    * `obj` (object): object to compress and serialize

  Returns:
    ``str``. 

  """
  #sys.setrecursionlimit(PICKLE_MAX_RECURSION_DEPTH)
  return zlib.compress(json.dumps(obj))

def jzloads(jzstr):
  """ Helper to uncompress and deserialize a json object
  using json and zlib

  Args:
    * `jzstr` (str): compressed and json serialized object

  Returns:
    ``object``. 

  Raises:
    ``ValueError``

  """
  #sys.setrecursionlimit(PICKLE_MAX_RECURSION_DEPTH)
  return json.loads(zlib.decompress(jzstr))

# Adapted from http://delete.me.uk/2005/03/iso8601.html
ISO8601_REGEX = re.compile(r"(?P<year>[0-9]{4})(-(?P<month>[0-9]{1,2})"
  r"(-(?P<day>[0-9]{1,2})((?P<separator>.)(?P<hour>[0-9]{2}):"
  r"(?P<minute>[0-9]{2})(:(?P<second>[0-9]{2})(\.(?P<fraction>[0-9]+))?)?"
  r"(?P<timezone>Z|(([-+])([0-9]{2}):([0-9]{2})))?)?)?)?")
TIMEZONE_REGEX = re.compile(r"(?P<prefix>[+-])(?P<hours>[0-9]{2})."
  r"(?P<minutes>[0-9]{2})")

class ParseError(Exception):
  """Raised when there is a problem parsing a date string"""

def decode_datetime(datestring):
  """ Take an ISO8601 string and convert to datetime object
  Its either <div data-date="2010-09-15T15:44:43Z" class="iso8601" 
  title="2010-09-15T15:44:43Z">2010-09-15T15:44:43Z</div>
  or 2010-09-14T20:30:22Z

  Args:
    * `datestring` (str,unicode): ISO8601 string %Y-%m-%dT%H:%M:%SZ

  Returns:
    ``datetime.datetime``.

  """
  # Remove any html
  datestring = strip_tags(datestring)

  try:
    dateobject = datetime.strptime(datestring, '%Y-%m-%dT%H:%M:%SZ')
  except ValueError:
    raise

  return dateobject

def timestamp_to_datetime(timestamp):
  """ Convert Javascript timestamp to UTC datetime object 
  we can store in the DB

  Args:
    * `timestamp` (basestring, float, int): Timestamp

  Returns:
    ``.

  """
  try:
    return datetime.utcfromtimestamp(float(timestamp)/1000)
  except (ValueError, TypeError):
    # timestamp could be 'null' or ''
    return ''

def to_user_time(date_time, all_day):
  """ Return unix timestamp in user's timezone.  If event is 
  all_day times don't matter so we don't convert.

  Args:
    * `date_time` (): 
    * `all_day` (): 

  Returns:
    ``.

  """
  if all_day:
    return time.mktime(date_time.timetuple())
  elif date_time:
    date_time = pytz.utc.localize(date_time)
    return calendar.timegm(date_time.timetuple())

  return ''

def to_tz_hours(user_tz):
  """ Take a timezone string and convert to hours
  US/Central to -500

  Args:
    * `user_tz` ():

  Returns:
    `str`

  """
  timezone = pytz.timezone(user_tz)
  return timezone.localize(datetime.utcnow()).strftime('%z')

def wrap_html(iso_string, class_, date_string, style):
  """ Return an html wrapped version of date

  """
  if style:
    style = 'style="{0}"'.format(style)
  else:
    style = ''
  #return '<div data-date="{0}" class="{1}" title="{2}">{2}</div>'.format(
  #  iso_string, class_, date_string)
  return '<div {3} class="{1}" title="{2}">{2}</div>'.format(
      iso_string, class_, date_string, style)

def encode_datetime(dateobject, class_='iso8601', 
    tz_=None, add_html=True, style=None, return_object=False):
  """ ISO8601 RFC 3339 format

  Args:
    * `dateobject` (datetime,str,unicode): object to encode, should be UTC
    * `class_` (str): iso8601/
    * `tz_` (str): users timezone offset(America/Chicago, US/Central)
    * `add_html`(bool): wrap return iso string in html
    * `style`(str): extra style when using add_html. Add just in quotes part
    * `return_object `(bool): return datetime object or if not string

  Returns:
    ``str``. Datetime in ISO 8601/RFC 3339 format with surrounding html

  """
  if not dateobject:
    #dateobject = datetime.utcnow()
    return ''

  if type(dateobject) in (unicode, str):
    try:
      dateobject = parser.parse(dateobject)
    except (AttributeError, ValueError):
      try:
        dateobject = datetime.fromtimestamp(float(dateobject))
      except ValueError:
        try:
          dateobject = datetime.strptime(
              dateobject, '%Y-%m-%dT%H:%M:%SZ')
        except (TypeError, ValueError):
          #logging.info(dateobject)
          # its a string already in iso format
          #return wrap_html(dateobject, class_, dateobject)
          if not "<div" in dateobject and dateobject[-1] == "Z":
            if add_html:
              return wrap_html(
                  dateobject, 'iso8601', dateobject, style)
            else:
              return dateobject
          else:
            return dateobject

  # Offset datetime object by users timezone
  if tz_:
    dateobject = dateobject.replace(tzinfo=pytz.utc).astimezone(
        pytz.timezone(tz_))

  if return_object:
    return dateobject
  else:
    iso_string = dateobject.strftime('%Y-%m-%dT%H:%M:%SZ')
    date_string = ''
    if class_ == 'gridDate':
      #date_string = dateobject.strftime('%Y/%m/%d %H:%M')
      date_string = dateobject.strftime('%m-%d-%Y %I:%M %p')
      #date_string = iso_string
    elif class_ == 'iso8601':
      date_string = iso_string
    elif class_ == 'pdf':
      #date_string = dateobject.strftime('%Y-%m-%d')
      date_string = dateobject.strftime('%m-%d-%Y %I:%M %p %Z')

    if add_html:
      date_string = wrap_html(iso_string, class_, date_string, style)
    else:
      date_string = strip_tags(date_string)

    return date_string

def convert_bytes(bytes_):
  """Convert int total byte value to human readable

  Args:
    * `bytes_` (int): number of bytes to convert

  Returns:
    ``str``. Bytes in human readable form

  """
  if not bytes_:
    bytes_ = 0.0
  try:
    bytes_ = float(bytes_)
  except ValueError:
    bytes_ = 0.0
  if bytes_ >= 1099511627776:
    terabytes = bytes_ / 1099511627776
    size = '%.2f T' % terabytes
  elif bytes_ >= 1073741824:
    gigabytes = bytes_ / 1073741824
    size = '%.2f G' % gigabytes
  elif bytes_ >= 1048576:
    megabytes = bytes_ / 1048576
    size = '%.2f M' % megabytes
  elif bytes_ >= 1024:
    kilobytes = bytes_ / 1024
    size = '%.2f K' % kilobytes
  else:
    size = '%.2f B' % bytes_
  return size

def convert_datetime(dateitem, direction = 'string'):
  """ Takes a string or a date and converts it to a
  format JSON will accept (such as sessions)
  
  Args:
    * `dateitem` (str)(datetime): the item to convert
    * `dir` (str): What direction to Convert to. \
      It accepts 'string' (convert datetime TO string) (default option)
    or 'datetime' (convert string to datetime)
    
  Returns:
    ``str`` ``datetime``. The end result converted over
  """
  if (direction == 'string'):
    return dateitem.strftime('%b %d %Y %I:%M:%S%f%p')
  else:
    if dateitem:
      return datetime.strptime(dateitem, '%b %d %Y %I:%M:%S%f%p')

  return ''
  

ZERO = timedelta(0)
class Utc(tzinfo):
  """UTC

  """
  def utcoffset(self, dt):
    """SHEATS NEEDS TO DOCUMENT
    """
    return ZERO

  def tzname(self, dt):
    """SHEATS NEEDS TO DOCUMENT
    """
    return "UTC"

  def dst(self, dt):
    """SHEATS NEEDS TO DOCUMENT
    """
    return ZERO
UTC = Utc()

class FixedOffset(tzinfo):
  """Fixed offset in hours and minutes from UTC

  """
  def __init__(self, offset_hours, offset_minutes, name):
    self.__offset = timedelta(hours=offset_hours, minutes=offset_minutes)
    self.__name = name

  def utcoffset(self, dt):
    """SHEATS NEEDS TO DOCUMENT
    """
    return self.__offset

  def tzname(self, dt):
    """SHEATS NEEDS TO DOCUMENT
    """
    return self.__name

  def dst(self, dt):
    """SHEATS NEEDS TO DOCUMENT
    """
    return ZERO

  def __repr__(self):
    return "<FixedOffset %r>" % self.__name

def parse_timezone(tzstring, default_timezone=UTC):
  """ Parses ISO 8601 time zone specs into tzinfo offsets

  """
  if tzstring == "Z":
    return default_timezone
  # This isn't strictly correct, but it's common to encounter dates without
  # timezones so I'll assume the default (which defaults to UTC).
  # Addresses issue 4.
  if tzstring is None:
    return default_timezone
  m = TIMEZONE_REGEX.match(tzstring)
  prefix, hours, minutes = m.groups()
  hours, minutes = int(hours), int(minutes)
  if prefix == "-":
    hours = -hours
    minutes = -minutes
  return FixedOffset(hours, minutes, tzstring)

def parse_date(datestring, default_timezone=UTC):
  """ Parses ISO 8601 dates into datetime objects

  The timezone is parsed from the date string. However it is quite common to
  have dates without a timezone (not strictly correct). In this case the
  default timezone specified in default_timezone is used. This is UTC by
  default.
  """
  if not isinstance(datestring, basestring):
    raise ParseError("Expecting a string %r" % datestring)
  m = ISO8601_REGEX.match(datestring)
  if not m:
    raise ParseError("Unable to parse date string %r" % datestring)
  groups = m.groupdict()
  tz = parse_timezone(groups["timezone"], default_timezone=default_timezone)
  if groups["fraction"] is None:
    groups["fraction"] = 0
  else:
    groups["fraction"] = int(float("0.%s" % groups["fraction"]) * 1e6)
  return datetime(int(groups["year"]), int(groups["month"]), 
    int(groups["day"]), int(groups["hour"]), int(groups["minute"]), 
    int(groups["second"]), int(groups["fraction"]), tz)


def json_prep(obj):
  """Prepare any type of object for conversion to json by:
    1. Converting datetime objects to ISO8601 format.
  
  Returns:
    * A copy of the object

  """
  if isinstance(obj, dict):
    return_dict = {}
    for key, value in obj.items():
      return_dict[key] = json_prep(value)
    return return_dict
      
  if isinstance(obj, list):
    return_list = []
    for value in obj:
      return_list.append(json_prep(value))
    return return_list
  
  if isinstance(obj, datetime):
    return encode_datetime(obj, add_html=False)

  if isinstance(obj, DBRef):
    return obj.id

  if isinstance(obj, ObjectId):
    return str(obj)
  
  return obj

def utf8_prep(obj):
  """ Converting strings in object to utf8.  Used
  in importing to filter incompatible characters
  
  Returns:
    * A copy of the object

  """
  if isinstance(obj, dict):
    return_dict = {}
    for key, value in obj.items():
      try:
        key = unicode(key)
      except UnicodeDecodeError:
        key = Binary(obj)
      return_dict[key] = utf8_prep(value)
    return return_dict
      
  if isinstance(obj, list):
    return_list = []
    for value in obj:
      return_list.append(utf8_prep(value))
    return return_list

  if isinstance(obj, str):
    return unicode(obj, errors='ignore').encode('utf-8')
  elif isinstance(obj, unicode):
    return obj.decode('utf-8', 'replace')
  
  return obj

def binary_prep(obj):
  """ Binary encode special characters 

  """
  if isinstance(obj, dict):
    return_dict = {}
    for key, value in obj.items():
      try:
        key = unicode(key)
      except UnicodeDecodeError:
        key = Binary(obj)
      return_dict[key] = binary_prep(value)
    return return_dict
      
  if isinstance(obj, list):
    return_list = []
    for value in obj:
      return_list.append(binary_prep(value))
    return return_list

  if type(obj) in (str, unicode):
    try:
      return unicode(obj)
    except UnicodeDecodeError:
      return Binary(obj)
 
  return obj


def xor_crypt_string(data, key):
  """ XOR encryption/decryption of string for simple operations

  Args:
    * `data` (str): data to encrypt
    * `key` (str): key to use for encryption

  """
  new = ''
  length_of_key = len(key)
  position_in_key = 0 ## position in password

  for old_char in data:
    # Get new charactor by XORing bias against old character
    new_char = chr(ord(old_char) ^ ord(key[position_in_key]))  
 
    new = new + new_char
    position_in_key = (position_in_key + 1) % length_of_key
 
  return new

def random_string(string_length):
  """ Generate random string of length

  Args:
    * `string_length` (int):

  """
  letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  out_str = ''
  for idx in xrange(string_length):
    out_str += random.choice(letters)
  return out_str

def prep_request_args(args):
  """ Prepare default request arguments
  Also filter out items not needed like _xsrf, ajax

  Args:
    * `args` (dict): dict of key value=list arguments 
  Returns:
    ``dict``. 

  """
  new_args = {}
  for key, val in args.iteritems():
    if len(val) > 1:
      # Leave lists in place
      new_args[key] = val
    else:
      try:
        new_args[key] = unicode(val[0])
      except UnicodeDecodeError:
        new_args[key] = val[0]
    try:
      new_args[key] = json.loads(new_args[key])
    except (ValueError, TypeError):
      pass

  return new_args


def increase_id(val):
  """ Given a string or integer value get the next
  item in the sequence, only looks at alpha numeric characters
  all others stay the same

  alpha numeric sequence
  0-9 --> 48-57
  A-Z --> 65-90
  a-z --> 97-122

  Args:
    * val (str or int):id to increase

  Returns:
    * ``str``. increased value

  >>> increase_id('1')
  '2'
  >>> increase_id('1-2')
  '1-3'
  >>> increase_id('1-a')
  '1-b'
  >>> increase_id('1-A')
  '1-B'
  >>> increase_id('1-Z')
  '2-A'

  """
  new_val = val
  # Increment obj val and update 
  if isinstance(val, int) or val.isdigit():
    new_val = int(val) + 1
  else:
    new_val = list(reversed(list(new_val)))

    for idx, val in enumerate(new_val):
      ord_val = ord(val)
      if 48 <= ord_val <= 57:
        if ord_val == 57:
          new_val[idx] = '0'
        else:
          new_val[idx] = chr(ord_val + 1)
          break
      elif 97 <= ord_val <= 122:
        if ord_val == 122:
          new_val[idx] = 'a'
        else:
          new_val[idx] = chr(ord_val + 1)
          break
      elif 65 <= ord_val <= 90:
        if ord_val == 90:
          new_val[idx] = 'A'
        else:
          new_val[idx] = chr(ord_val + 1)
          break
    new_val = ''.join(reversed(new_val))

  return new_val

 
def print_timing(func):
  """ Performance evaluation decorator to get times for functions
  Usage:

    @libs.helpers.print_timing

  """
  def wrapper(*arg):
    """ Wrap function with time and print out total execution time

    """
    t1 = time.time()
    res = func(*arg)
    t2 = time.time()
    print '{0} took {1:-f} ms'.format(func.func_name, (t2-t1)*1000.0)
    return res

  return wrapper

def space_out_camel_case(string_as_camel_case):
  """Adds spaces to a camel case string.  Failure to space out
  string returns the original string.
  >>> space_out_camel_case('DMLSServicesOtherBSTextLLC')
  'DMLS Services Other BS Text LLC'
  """
  
  if not string_as_camel_case:
    return ''

  pattern = re.compile('([A-Z][A-Z][a-z])|([a-z][A-Z])')
  return pattern.sub(lambda m: m.group()[:1] \
    + ' ' + m.group()[1:], string_as_camel_case)


def ip_addr_range(start_addr, end_addr):
  """
  Note does not check start > end

  Args:
    * `start_addr` (str): valid ip string 10.0.0.1
    * `end_addr` (str): valid ip string 10.0.0.2

  """
  def incr_addr(addr_list):
    """ Increase the tuple address

    Args:
      * `addr_list` (list): list of split by . ip

    """
    addr_list[3] += 1
    for i in (3, 2, 1):
      if addr_list[i] == 256:
        addr_list[i] = 0
        addr_list[i-1] += 1

  def as_string(addr_list):
    """ Convert to string form

    """
    return ".".join(map(str, addr_list))

  start_addr_list = map(int, start_addr.split("."))
  end_addr_list = map(int, end_addr.split("."))

  cur_addr_list = start_addr_list[:]
  yield as_string(cur_addr_list)
  for i in range(4):
    while cur_addr_list[i] < end_addr_list[i]:
      incr_addr(cur_addr_list)
      yield as_string(cur_addr_list)


def get_list_of_ips_from_ranges(ranges):
  """ Given a string of ranges in the form
  209.34.76.0-209.34.76.255
  209.34.84.0-209.34.84.255
  Generate a list of potential ips

  Args:
    * `ranges` (str): line by line dash separated list of ip ranges

  """
  range_list = []
  ranges = [ran_.strip() for ran_ in ranges.split('\n') if ran_]
  ranges = [ran_.split('-') for ran_ in ranges if ran_]

  for range_ in ranges:
    if len(range_) == 2:
      start = range_[0]
      end = range_[1]
      range_list.append(start)
      for addr in ip_addr_range(start, end):
        if addr not in range_list:
          range_list.append(addr)

  return range_list

def fix_bad_keys(old_dict):
  """ Recursively remove "."s from key names
  
  Args:
    * `old_dict` (dict): 
  """
  new_dict = {}
  for key, val in old_dict.items():
    new_key = key.replace('.', '_')
    if isinstance(val, dict):
      new_dict[new_key] = fix_bad_keys(val)
    else:
      new_dict[new_key] = val
  return new_dict


# pylint: disable-msg=W0703,R0903,E0702
class Retry(object):
  """ The retry decorator reruns a funtion tries 
  times if an exception occurs.

  Attributes:
    `default_exceptions` (Exception): 

  Usage:

    >>> from retry_decorator import Retry
    >>> @Retry(2)
    ... def fail_fn():
    ...   raise Exception("failed")
    ... 
    >>> fail_fn()
    Retry, exception: failed
    Retry, exception: failed
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "retry_decorator.py", line 32, in fn
      raise exception
    Exception: failed
      
  """
  default_exceptions = (Exception)

  def __init__(self, tries, exceptions=None, delay=0):
    """
    Decorator for retrying a function if exception occurs
    
    tries -- num tries 
    exceptions -- exceptions to catch
    delay -- wait between retries
    """
    self.tries = tries
    if exceptions is None:
      exceptions = Retry.default_exceptions
    self.exceptions =  exceptions
    self.delay = delay

  def __call__(self, f):
    """ _

    """
    def fn(*args, **kwargs):
      """ _

      """
      exception = None
      for _ in range(self.tries):
        try:
          return f(*args, **kwargs)
        except self.exceptions, e:
          print "Retry, exception: "+str(e)
          time.sleep(self.delay)
          exception = e
      #if no success after tries, raise last exception
      raise exception
    return fn


###############################################################################
# Begin custom logger
###############################################################################
# For logging to the console
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
#The background is set with 40 plus the number 
# of the color, and the foreground with 30

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {
  'WARNING': YELLOW,
  'INFO': WHITE,
  'DEBUG': BLUE,
  'CRITICAL': YELLOW,
  'ERROR': RED
}

def formatter_message(message, use_color=True):
  """
  Args:

  """
  if use_color:
    message = message.replace('$RESET', RESET_SEQ).replace(
        '$BOLD', BOLD_SEQ)
  else:
    message = message.replace('$RESET', '').replace('$BOLD', '')
  return message

class ColorFormatter(logging.Formatter):
  """ _

  """
  def __init__(self, msg, use_color=True):
    """ _

    """
    logging.Formatter.__init__(self, msg)
    self.use_color = use_color

  def format(self, record):
    """ _

    """
    levelname = record.levelname
    if self.use_color and levelname in COLORS:
      levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + \
          levelname + RESET_SEQ
      record.levelname = levelname_color
    return logging.Formatter.format(self, record)


class ColorLogger(logging.Logger):
  """ Custom logger class with multiple destinations
    

  """
  FORMAT = """[$BOLD%(name)-20s$RESET][%(levelname)-18s]  """ \
    """%(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"""
  COLOR_FORMAT = formatter_message(FORMAT, True)

  def __init__(self, name):
    """ _

    """
    logging.Logger.__init__(self, name, logging.DEBUG)        

    color_formatter = ColorFormatter(self.COLOR_FORMAT)

    console = logging.StreamHandler()
    console.setFormatter(color_formatter)

    self.addHandler(console)
    return


def logit(msg, log, jobevent=None):
  """ Logging helper.

  Args:
    * `msg` (str):
    * `log` (logging):
    * `jobevent` (Threading.event):
  
  """
  log.info(msg)
  if jobevent:
    jobevent.status(msg)

def parse_vcard(lines):
  """ Returns a message with timestamp

  Args:
    `lines` (list): vcard file lines
  Returns:
    ``dict``.

  """
  vcard = {
    'First Name':'',
    'Last Name':'',
    'Company':'',
    'Title':'',
    'Email':'',
    'Work Phone':'',
    'Home Phone':'',
    'Address Work':'',
    'Address Home':'',
  }

  if isinstance(lines, basestring):
    lines = lines.split('\n')
  for line in lines:
    if re.match('N.*:.*', line):
      try:
        val = line.split(':')[1]
        name = val.split(';')
        vcard['First Name'] = name[1]
        vcard['Last Name'] = name[0]
      except IndexError:
        pass

    if re.match('EMAIL.*:.*', line):
      try:
        val = line.split(':')[1]
        vcard['Email'] = val
      except IndexError:
        pass

    if re.match('ORG.*:.*', line):
      try:
        val = line.split(':')[1]
        vcard['Company'] = val
      except IndexError:
        pass

    if re.match('TITLE.*:.*', line):
      try:
        val = line.split(':')[1]
        vcard['Title'] = val
      except IndexError:
        pass

    if re.match('TEL.*:.*', line):
      try:
        val = line.split(':')[1]
        if 'WORK' in line:
          vcard['Work Phone'] = val
        else:
          vcard['Home Phone'] = val
      except IndexError:
        pass

    if re.match('ADR.*:.*', line):
      try:
        val = line.split(':')[1].split(';')
        if 'WORK' in line:
          vcard['Address Work'] = ' '.join(val).strip()
        else:
          vcard['Address Home'] = ' '.join(val).strip()
      except IndexError:
        pass

  return vcard

mobile_b = re.compile(r"""
  smartphone|android|iphone|ipad|ipod|avantgo|blackberry|blazer|compal|
  elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|
  mmp|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|
  symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|
  xda|xiino""", re.I|re.M)

mobile_v = re.compile(r"""
  1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|
  ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|
  au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|
  bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|
  da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|
  em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|
  gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|
  hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|
  i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|
  ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|
  kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|e\\-|e\\/|\\-[a-w])|libw|lynx|
  m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(di|rc|ri)|
  mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|
  mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|
  tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|
  pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|
  psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|
  rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|
  se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|
  sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|
  t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|
  to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|
  vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|
  vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|
  wmlb|wonu|x700|xda(\\-|2|g)|yas\\-|your|zeto|zte\\-""", re.I|re.M)


def is_mobile(request):
  """ Checks if request is from a mobile device

  Args:
    `lines` (list): vcard file lines
  Returns:
    ``dict``.

  """
  is_mobile = False
  user_agent = request.headers.get('User-Agent')
  if user_agent:
    if mobile_b.search(user_agent) or mobile_v.search(user_agent[0:4]):
      is_mobile = True

  return is_mobile

class DictDiffer(object):
  """ Calculate the difference between two dictionaries as:
  (1) items added
  (2) items removed
  (3) keys same in both but changed values
  (4) keys same in both and unchanged values
  >>> a = {'a': 1, 'b': 1, 'c': 0}
  >>> b = {'a': 1, 'b': 2, 'd': 0}
  >>> d = DictDiffer(b, a)
  >>> print "Added:", d.added()
  Added: set(['d'])
  >>> print "Removed:", d.removed()
  Removed: set(['c'])
  >>> print "Changed:", d.changed()
  Changed: set(['b'])
  >>> print "Unchanged:", d.unchanged()
  Unchanged: set(['a'])
  """
  def __init__(self, current_dict, past_dict):
    self.current_dict, self.past_dict = current_dict, past_dict
    self.set_current, self.set_past = \
        set(current_dict.keys()), set(past_dict.keys())
    self.intersect = self.set_current.intersection(self.set_past)

  def added(self):
    return self.set_current - self.intersect 

  def removed(self):
    return self.set_past - self.intersect 

  def changed(self):
    return set(o for o in self.intersect if \
        self.past_dict[o] != self.current_dict[o])

  def unchanged(self):
    return set(o for o in self.intersect if \
        self.past_dict[o] == self.current_dict[o])

