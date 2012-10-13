#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=

""" Worker helper, used to offload work to another thread

.. moduleauthor:: <>

"""

import tornado.escape
import tornado.httpclient
import json
import re
import conf
import Queue
import threading
import logging
import libs.helpers
import os

class WorkerThreadBase(threading.Thread):
  """ Derive from this base worker thread

  Attributes:
    `_worker_q` (Queue.Queue):

  """

  _worker_q = None

  def __init__ (self):
    """ Initialize a global mongo connection on creation

    """
    #self._sleepperiod = 1.0

    self._worker_q = Queue.Queue()

    threading.Thread.__init__(self)


  def stop(self, timeout=None):
    """ Stop the thread

    """
    self._worker_q.put({'exit':True})
    threading.Thread.join(self, timeout)

  def put(self, info):
    """ Add items to the internal Queue

    Args:
      `info` (dict): which method to put in the internal queue

    """
    self._worker_q.put(info)


class WorkerThread(WorkerThreadBase):
  """This is a global worker queue to offload long running processes
  Things like analytics can be added to this queue to help processing
  and prevent slowdowns in the request pipeline

  """

  def __init__ (self):
    """ Initialize a global mongo connection on creation

    """
    self.http_client = tornado.httpclient.HTTPClient()

    super(WorkerThread, self).__init__()

  def run(self):
    """Run the task queue

    """
    logging.info('Worker thread is running. ' + str(self.__hash__()))

    while True:
      msg = self._worker_q.get()

      if 'exit' in msg:
        logging.info('Exiting worker queue')
        break

      if 'stop' in msg:
        pass

      # do a long running task...
      # logging.info(str(msg))

      if 'xx' in msg:
        print msg
      
      self._worker_q.task_done()

