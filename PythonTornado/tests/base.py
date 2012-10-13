import unittest
import random
import uuid
import json

import sys
import os
sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))

from main import HANDLERS
import models.root
import conf

from libs.helpers import encode_datetime

import mechanize
import cookielib

class TestBase(unittest.TestCase):
  """Base test case all other tests should inherit from

  """
  LOCAL_URL = 'http://localhost:8000'
  def get_url(self, name):
    """ Helper function for unit tests to get url from named handler

    Args:
      * `name` (str): handler name

    """    
    for defn in HANDLERS: 
      if defn.name == name:
        return defn._path

    raise Exception('Handler name not found')

  def setUp(self):

    # Browser
    self.br = mechanize.Browser()

    # Cookie Jar
    self.cj = cookielib.LWPCookieJar()
    self.br.set_cookiejar(self.cj)

    # Browser options
    self.br.set_handle_equiv(True)
    #self.br.set_handle_gzip(True)
    self.br.set_handle_redirect(True)
    self.br.set_handle_referer(True)
    self.br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    self.br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Want debugging messages?
    self.br.set_debug_http(False)
    self.br.set_debug_redirects(True)
    self.br.set_debug_responses(True)
        
    # User-Agent (this is cheating, ok?)
    self.br.addheaders = [
        ('User-agent', 
         'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')
      ]

    # The site we will navigate into, handling it's session
    self.br.open(self.LOCAL_URL + self.get_url('login'))
    jar = self.br._ua_handlers['_cookies'].cookiejar
    xsrf = jar._cookies['localhost.local']['/']['_xsrf'].value
    self.br.xsrf = xsrf

    try:
      self.testuser = models.user.User.find_one({'email': 'test@site.com'})
    except:
      print 'NEED TO MAKE A test@site.com user with non-staff privelages'
      exit()

  def tearDown(self):
    self.logout()

  def logout(self):
    self.br.open(self.LOCAL_URL + self.get_url('logout'))

  def login(self, su=True, user=None, password=None):
    # The site we will navigate into, handling it's session
    response = self.br.open(self.LOCAL_URL + self.get_url('login'))

    # Select the first (index zero) form
    self.br.select_form(nr=0)

    if user is not None and password is not None:
      self.br.form['email'] = user
      self.br.form['pw'] = password
    else:
      # User credentials
      self.br.form['email'] = conf.USER_GENERIC['email']
      self.br.form['pw'] = conf.USER_GENERIC['pw']

    # Login
    self.br.submit()

