#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=

"""Define auth handlers

.. moduleauthor:: <>

"""
import logging
import copy
from datetime import datetime
import tornado.web
import uuid
import tornado.httpclient

import handlers.base

class AuthLoginHandler(handlers.base.BaseHandler):
  """ Handle login events to the system

  """
  def get(self):
    """ Display the login page. All unauthorized traffic 
    goes here and redirects after successful post.

    """
    if not self.current_user:
      nxt = '?next=' + tornado.escape.url_escape(self.get_argument('next', '/'))
      self.render('auth.html', nxt=nxt, errors=None)
    else:
      self.redirect('/')

  def post(self):
    """ Send request for login to system 

    Returns:
      Return page with errors or validate and move to next url 
      found in GET ?next=

    """
    self.render('auth.html', nxt=nxt, errors='Invalid login.')

class AuthLogoutHandler(handlers.base.BaseHandler):
  """ Log a user out

  This just clears cookies and session and redirects the user to login

  """
  def get(self):
    """ Delete the user session and cookie and redirect to the login page

    """
    if self.current_user and self.cookies.get('session'):
      cookies = {'session': self.cookies['session']}
       
    self.delete_session(self.current_user)
    self.clear_all_cookies()
    
    self.redirect(self.reverse_url('login'))

