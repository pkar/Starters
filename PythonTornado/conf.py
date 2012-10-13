#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=

""" Define a set of defaults for the application

.. module:: conf 
   :platform: Unix
   :synopsis: Define system globals

.. moduleauthor:: <>

"""
import os
import sys
import logging

DEBUG = True

###############################################################################
# System Paths
###############################################################################
ROOT_DIR = os.path.dirname(__file__)
logging.info('ROOT_DIR {0}'.format(ROOT_DIR))
LOCAL = True # Change to false for production

ROOT_STATIC_DIR = os.path.join(ROOT_DIR, 'static')
TEMPLATE_PATH = os.path.join(ROOT_DIR, 'templates')
STATIC_PATH = os.path.join(ROOT_DIR, 'static')
TMP_PATH = os.path.join(ROOT_DIR, 'tmp')
LOG_PATH = os.path.join(ROOT_DIR, '_log')
SUPPORT_EMAILS = 'user@site.com'

COFFEE_FILES = [
  'coffee/main.coffee',
]

JS_LIBS = None

if LOCAL:
  JS_LIBS = [
    'libs/jquery-1.8.2.js',
    'libs/underscore-min.js',
    'libs/underscore.string.min.js',
    'libs/backbone.js',
    'libs/bootstrap2.1.0/js/bootstrap.js',
    'libs/jstorage.js',
  ]
else:
  JS_LIBS = [
    'libs/jquery-1.8.2.min.js',
    'libs/underscore-min.js',
    'libs/underscore.string.min.js',
    'libs/backbone-min.js',
    'libs/bootstrap2.1.0/js/bootstrap.min.js',
    'libs/jstorage.min.js',
  ]

JS = [
  'js/main.js',
]

