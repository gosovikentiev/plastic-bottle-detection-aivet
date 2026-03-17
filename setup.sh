#!/bin/bash

pip install -r requirements.txt
DIR=$(pwd)
(crontab -l 2>/dev/null; echo "@reboot python3 $DIR/obstacleavoidance.py") | crontab -
