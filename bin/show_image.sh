#!/bin/bash

/usr/bin/killall -q -9 fbi

FBI="/usr/bin/fbi -T 2 -d /dev/fb0 -noverbose --readahead --nocomments -a"

($FBI $1 2>&1) >/dev/null

