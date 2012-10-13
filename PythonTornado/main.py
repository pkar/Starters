#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=

"""This is the entry point to the application.

.. moduleauthor:: <>

"""

import re
import os.path
import logging # debug,info,warning,error,critical
from multiprocessing import Pool, Queue
import subprocess
import signal

import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
tornado.options.enable_pretty_logging()
import tornado.web

import libs.worker
import handlers.auth
import handlers.base
import libs.helpers

import conf
 
from tornado.options import define, options
from libs.datastructures import SortedDict
 
define("port", default=8000, help="run on the given port", type=int)

WORKER = libs.worker.WorkerThread()

URL = tornado.web.url

# Handlers are defined using URLSpec objects and contain names along
# with kwargs metadata which is used to generate javascript
HANDLERS = [

  URL(r'/', 
    handlers.base.HomeHandler,
    #kwargs={'type': 'home'},
    name='home'),

  URL(r'/auth/login', 
    handlers.auth.AuthLoginHandler,
    #kwargs={},
    name='login'),

  URL(r'/auth/logout', 
    handlers.auth.AuthLogoutHandler,
    #kwargs={},
    name='logout'),

]


class Application(tornado.web.Application):
  """Default application settings defined here

  Attributes:
    * `js_css` (dict): list of javascript and css to load
    * `conf` (module): configuration module
    * `helpers` (module): libs.helpers module

  """
  js_css = None
  conf = None
  helpers = None
  worker_q = None

  def __init__(self):
    """

    """
    settings = dict(
      template_path=conf.TEMPLATE_PATH,
      static_path=conf.STATIC_PATH,
      tmp_path=conf.TMP_PATH,
      xsrf_cookies=True,
      cookie_secret="1toETllK#/Vo=",
      login_url='/auth/login',
      debug=conf.DEBUG,
      #1200 seconds is 20 minutes, 24 hours 86400, 604800 1 week
      session_expire=604800,
      pool=Pool(4),
      queue=Queue(),
      autoescape=None,
      # The following may be the same
    )

    self.conf = conf

    logging.info('Initializing app worker thread')
    WORKER.start()
    # Start up the worker queue
    self.worker_q = WORKER

    self.helpers = libs.helpers

    # compress javascript on the fly, for admin sections
    logging.info('Starting server with these settings {0}'.format(settings))
    tornado.web.Application.__init__(self, HANDLERS, **settings)

  def __del__(self):
    """ Destructor needs to kill worker q

    """
    try:
      # Kill worker queue
      logging.info('Stopping worker threads')
      WORKER.stop()
    except AttributeError:
      pass

def main():
  """Run server instance

  """
  tornado.locale.load_translations(os.path.join(conf.ROOT_DIR, "translations"))
  tornado.options.parse_command_line()

  http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
  http_server.listen(options.port)
  logging.info('Starting server on port {0}'.format(options.port))
  ioloop = tornado.ioloop.IOLoop.instance()

  try:
    ioloop.start()
  except (KeyboardInterrupt, SystemExit):
    logging.info('Interrupt, exiting worker thread and application')
    WORKER.stop()
    exit()
  
if __name__ == '__main__':
  main()
