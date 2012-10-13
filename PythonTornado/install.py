#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import sys
import subprocess

def install_common():
  subprocess.Popen([""" 
    #git config --global user.name "Your Full Name"
    #git config --global user.email "Your Email Address"

    sudo chown -R $USER /usr/local
    npm -g install coffee-script
    npm -g install uglify-js
    npm -g install less
    
    sudo easy_install -U pip
    sudo pip install virtualenv virtualenvwrapper
    pip install --user --upgrade fabric
    pip install --user --upgrade tornado

  """], shell=True).wait()

def install_mac():
  # Check for gcc and xcode command line tools
  try:
    subprocess.Popen(['gcc'], 
        stdout=subprocess.PIPE, 
        stdin=subprocess.PIPE, 
        stderr=subprocess.PIPE)
  except OSError:
    raise Exception("Requires macports and xcode dev tools to be installed")

  subprocess.Popen([""" 
    # install brew
    sudo chown -R $USER /usr/local
    ruby -e "$(curl -fsSkL raw.github.com/mxcl/homebrew/go)"
    brew update
    brew upgrade
    brew install node
    curl https://npmjs.org/install.sh | sh
    brew install wget
    brew install git
    brew install ack
    brew install imagemagick
    brew cleanup
    pip install --user --upgrade ipdb
    pip install --user --upgrade ipython
    pip install --user --upgrade mechanize
    sudo easy_install pylint
  """], shell=True).wait()

def install_linux():
  subprocess.Popen([""" 
    sudo apt-get --yes update
    sudo apt-get --yes upgrade
    sudo apt-get install python-setuptools
    sudo apt-get --yes install wget
    sudo apt-get --yes install htop
    sudo apt-get --yes install discus
    sudo apt-get --yes install build-essential
    sudo apt-get --yes install python-dev
    sudo apt-get --yes install git-core
    sudo apt-get --yes install imagemagick

    # Install node
    sudo apt-get install python-software-properties
    sudo add-apt-repository ppa:chris-lea/node.js
    sudo apt-get update
    sudo apt-get install nodejs npm

  """], shell=True).wait()


if __name__ == "__main__":
  if sys.platform == 'darwin':
    install_mac()
  else:
    install_linux()
  install_common()
