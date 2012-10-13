#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable-msg=

""" Define a base handler to initialize all requests

All handlers inherit from the BaseHandler

.. moduleauthor:: <>

"""

import sys 
import re
import zlib
import traceback
import logging
import httplib
import urllib
import threading
import json
import datetime 
import uuid 

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import tornado.web
import tornado.websocket
import tornado.escape
import tornado.locale
import tornado.httpclient
import smtplib

import libs.helpers 

class ThreadableMixin:
  """

  If we need to redirect it to _worker () set the variable 
  self.redir to the right url. If we need json for ajax request, 
  then in self.res instead of the generated page assign a formed 
  dict with the data.

  class Handler(tornado.web.RequestHandler, ThreadableMixin):
    def _worker(self):
      self.res = self.render_string("template.html",
        title=_("Title"), 
        data=self.application.db.query(
          "select ... where object_id =% s", self.object_id)
      )

    @tornado.web.asynchronous
    def get (self, object_id): 
      self.object_id = object_id
      self.start_worker()

  """
  def start_worker(self):
    threading.Thread(target=self.worker).start()
 
  def worker(self):
    try:
      self._worker()
    except tornado.web.HTTPError, e:
      self.set_status(e.status_code)
    except:
      logging.error("_worker problem ", exc_info=True)
      self.set_status(500)
    tornado.ioloop.IOLoop.instance().add_callback(
      self.async_callback(self.results)
    )

  def results (self):
    if self.get_status() != 200:
      self.send_error(self.get_status ())
      return
    if hasattr(self, 'res'):
      self.finish (self.res)
      return
    if hasattr(self, 'redir'):
      self.redirect(self.redir)
      return
    self.send_error(500)

class SocketHandler(tornado.websocket.WebSocketHandler):
  """

  """
  waiters = list()
  cache = []
  cache_size = 200

  def allow_draft76(self):
    # for iOS 5.0 Safari
    return True

  def open(self):
    """

    """
    SocketHandler.waiters.append(self)

  def on_close(self):
    """

    """
    SocketHandler.waiters.remove(self)

  @classmethod
  def update_cache(cls, msg):
    """

    """
    cls.cache.append(msg)
    if len(cls.cache) > cls.cache_size:
      cls.cache = cls.cache[-cls.cache_size:]

  @classmethod
  def send_updates(cls, msg):
    """

    """
    logging.info("sending message to %d waiters", len(cls.waiters))
    for waiter in cls.waiters:
      try:
        waiter.write_message(msg)
      except:
        logging.error("Error sending message", exc_info=True)

  def on_message(self, message):
    """

    """
    logging.info("got message %r", message)
    parsed = json.loads(message)
    msg = {
      'id': str(uuid.uuid4()),
      'body': parsed['body'],
    }
    msg['html'] = self.render_string('message.html', message=msg)

    SocketHandler.update_cache(msg)
    SocketHandler.send_updates(msg)


class ErrorHandler(tornado.web.RequestHandler):
  """ Provide email on system errors.

  """

  def _handle_request_exception(self, err):
    """Send out an email on internal server errors
    during runtime

    Args:
      * `err` (HTTPError, Exception):

    """
    email_info = None
    status_code = 405
    if hasattr(err, 'status_code'):
      status_code = err.status_code

    if not 400 < status_code < 405:
      exc_type, exc_value, exc_traceback = sys.exc_info()
      tb_ = traceback.format_tb(exc_traceback)
      tb_plain = self._request_summary() + '\n\n' + ''.join(tb_)

      if self.current_user:
        pre = """ 
          User ID: {0}\n
          Email: {1}\n
          Exception: {3}\n
          Request: {4}\n
          Arguments: {5}\n
          """.format(
              self.current_user.get('_id'),
              self.current_user.get('Email'), 
              str(err),
              str(self.request),
              str(self.request.arguments),
              )
        tb_plain = pre + tb_plain + \
          '\n' + str(exc_type) + ':' + str(exc_value)

      logging.error(str(err) + tb_plain)

      tb_html = tb_plain.replace('\n', '<br/>')
      
      email_info = {
        'from':'mrbojangles@' + self.request.host.replace('https://', ''),
        'email':self.application.conf.SUPPORT_EMAILS,
        'subject':'Exception raised on ' + self.request.host + \
            ':' + str(exc_type) + ':' + str(exc_value),
        'body_html': tb_html,
        'body_plain': tb_plain,
      }

    if email_info:
      # Send here...
      pass

    super(ErrorHandler, self)._handle_request_exception(err)
 

class BaseHandler(ErrorHandler, ThreadableMixin):
  """Base, all other handlers inherit from here

  Attributes:
    * `current_section` (dict): section info for this request
    * `args` (dict): custom args object, converts request args

  """

  # Custom args compatible with django forms
  args = {}
  is_mobile = False

  @property
  def conf(self):
    """The main configuration file loaded at app start

    Returns:
      ``module conf``. The conf mondule

    >>> self.conf.SUPERUSER

    """
    return self.application.conf

  #def render_string(self, template_name, **kwargs):
  #  """ Generate the given template with the given arguments.
  #  We return the generated string. To generate and write a template
  #  as a response, use render() above.
  #  NOTE override to strip extra white space
  #  """
  #  html = super(BaseHandler, self).render_string(template_name, **kwargs)
  #  html = re.sub(r'>\s+<', '><', html)
  #  html = re.sub(r'\s+<', ' <', html)
  #  html = re.sub(r'>\s+', '> ', html)
  #  # IE css conditional, this needs to be fixed <!--[if IE 7]> <![endif]-->
  #  #html = re.sub(r'<!--(.|\s)*?-->', ' ', html)
  #  return html

  def on_finish(self):
    """ Overload default on_finish and add analytics after

    """
    pass
 
  def check_xsrf_cookie(self):
    """ Incase there are urls to skip POST xsrf checks
    add them here
    
    """
    super(BaseHandler, self).check_xsrf_cookie()

  def prepare(self):
    """ Do any pre initializing of the request before being executed
    A request for /auth/logout is ignored

    A new attribute is created self.args which removes the list and 
    makes it easier to deal with django forms
    The current section is initialized as well. 

    """
    super(BaseHandler, self).prepare()

    # Ignore prep for a logout request
    if self.request.path == self.reverse_url('logout'):
      return

    # Reset attributes
    self.args = {}

    self.args = libs.helpers.prep_request_args(self.request.arguments)

    self.is_mobile = libs.helpers.is_mobile(self.request)

  def get_current_user(self):
    """Get the current user session object

    This is an extracted json object pulled from Redis based
    on the cookie id

    Returns:
      ``dict``. Contains user information

    """
    key = self.get_secure_cookie('user')

    try:
      return libs.helpers.jzloads(self.db.get(key))
    except (TypeError, AttributeError):
      return None
  
  def get_user_locale(self):
    """Override the base locale

    TODO Fix return value set to user browser locale

    Returns:
      ``?``.

    """
    if self.current_user and 'locale' in self.current_user:
      #return tornado.locale.get('es_LA')
      return tornado.locale.get(self.current_user['locale'])

    # Return the browser locale
    return self.get_browser_locale()

  def create_session(self, user):
    """ On login initalize a user session

    >>> self.create_session(user=self.current_user)

    """
    logging.info('Creating session')
    user = {}

    return user

  def delete_session(self, user=None):
    """Remove a session from Redis

    Args:
      * `user`: user session object

    >>> self.delete_session()

    """
    if user:
      pass

class HomeHandler(BaseHandler):

  def get(self):
    self.render('index.html')

