#!/usr/bin/env bash
sudo apt-get update
sudo apt-get install python-setuptools
sudo apt-get install python-dev
sudo apt-get install libsctp-dev
sudo apt-get install git
git clone https://github.com/philpraxis/pysctp.git
cd pysctp
sudo python setup.py install
cd cd pysctp/build/lib.linux-x86_64-2.7/


