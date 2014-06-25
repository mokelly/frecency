#!/bin/bash

cd ~
sudo apt-get update
sudo apt-get -yqqu install git
sudo apt-get -yqqu install python-pip
sudo apt-get -yqqu install python-dev
sudo pip install -r /vagrant/requirements.txt --upgrade

cd /vagrant

sudo python setup.py develop
