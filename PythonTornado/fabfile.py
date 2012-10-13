#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Define methods for installation and updating of application and 
its requirements.

"""
import getopt
import os
import stat
import sys
import tarfile
import conf
import subprocess
import logging
sys.path.append(os.path.abspath('.'))

try:
  from fabric.api import *
except ImportError:
  print 'Please install Fabric first.'
  exit()

###############################################################################
# Development commands
###############################################################################
def update_tornado():
  """ Gets the latest version of tornado from git

  """
  start_dir = os.getcwd()
  subprocess.Popen([""" 
    mkdir -p tmp
    cd tmp
    git clone git://github.com/facebook/tornado.git
    cd tornado
    python setup.py build
    sudo python setup.py install
    cd ..
    sudo rm -rf tornado
    cd ..
  """], shell=True).wait()
  os.chdir(start_dir)

def update_git():
  """ To work with github, git needs to be latest version
  sudo add-apt-repository ppa:git-core/ppa
  sudo apt-get update
  sudo apt-get install git
  """

def run_coffee():
  """ NOT USED, compiled in main.py periodic loop

  """
  subprocess.Popen(["""
    coffee --bare --watch --lint --output static/js/ --compile coffee/
    """], shell=True).wait()

def run_uglify():
  """ Compresses js files, then combines them into a min file.
  Compile less and css files.

  """

  print ' '.join(['static/{0}'.format(js_) for js_ in conf.JS_LIBS])
  print ' '.join(['static/{0}'.format(js_) for js_ in conf.JS])
  subprocess.Popen(["""
    cat {0} > static/js/libs.min.js;
    cat {1} > static/js/main.min.js;
    uglifyjs --overwrite -v static/js/libs.min.js;
    uglifyjs --overwrite -v static/js/main.min.js;
    """.format(
      ' '.join(['static/{0}'.format(js_) for js_ in conf.JS_LIBS]),
      ' '.join(['static/{0}'.format(js_) for js_ in conf.JS_MAIN]),
    )], shell=True)

def run_main():
  """

  """
  subprocess.Popen(["""  
    python main.py
    """], shell=True).wait()


###############################################################################
# Testing
###############################################################################
PYLINTFILES = (
  'conf.py',
  'main.py',
  'libs/datastructures.py',
  'libs/helpers.py',
  'libs/worker.py',
  'models/root.py',
  'handlers/auth.py',
  'handlers/base.py',
)

JSLINTFILES = (
  'static/js/main.js',
)

TESTFILES = (
  'tests/test.py',
)

def lint():
  """Run pylint and jslint on files that have changed since 
  last commit -- but only if they are in PYLINTFILES or JSLINTFILES 
  """
  hg_status = local('hg status', capture=True)
  files = map(lambda x: x.split(' ')[-1], hg_status.split('\n'))
  pylintfiles = []
  jslintfiles = []
  for f in files:
    if f in PYLINTFILES:
      pylintfiles.append(f)
    if f.endswith('.js'):
      js_file = f.split('/')[-1]
      if js_file in JSLINTFILES:
        jslintfiles.append(js_file)
  for lintfile in pylintfiles:
    local('pylint {0}'.format(lintfile), capture=False)

  for lintfile in JSLINTFILES:
    local('gjslint {0}'.format(lintfile), capture=False)

def lint_js():
  """ _

  """
  for lintfile in JSLINTFILES:
    local('gjslint {0}'.format(lintfile), capture=False)

def lint_python():
  """ _

  """
  for lintfile in PYLINTFILES:
    local('pylint {0}'.format(lintfile), capture=False)

def lint_full():
  """ _

  """
  lint_python()
  lint_js()

def tests():
  for test in TESTFILES:
    local("""python {0}""".format(test), capture=False)

def usage():
  print \
    """
    Usage: python fabfile.py [option]

      -h, --help: show usage
      -i, --install: run the installation

    """

if __name__ == "__main__":

  try:
    opts, args = getopt.getopt(sys.argv[1:], "hi", [ \
            "help",
            "install", 
            ]
            )
  except getopt.GetoptError, err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    sys.exit(2)

  output = None
  if opts:
    for o, a in opts:
      if o in ("-h", '--help'):
        usage()
      elif o in ("-i", '--install'):
        print 'Running installation.'
        subprocess.Popen([""" 
        python install.py
        """], shell=True).wait()
        print 'done.'
      else:
        assert False, "unhandled option"
  else:
    usage()
    
