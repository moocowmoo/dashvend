#!/bin/bash

# relay pinouts are inverted
ON=0
OFF=1

DEV=/sys/class/gpio
RELAY=$DEV/gpio6
LIGHT=$DEV/gpio5

function flash_light(){
    echo $ON  > $LIGHT/value ; sleep .5 ;
    echo $OFF > $LIGHT/value ; sleep .5 ;
};

# initialize gpio directories
if [ ! -e $DEV/gpio5 ] ; then echo 5 > $DEV/export ; fi
if [ ! -e $DEV/gpio6 ] ; then echo 6 > $DEV/export ; fi

# initialize pin outputs
echo out > $RELAY/direction
echo out > $LIGHT/direction

# toggle dispensing relay
( echo $ON > $RELAY/value ; sleep .3 ; echo $OFF > $RELAY/value) &

# flash sign lights
( for x in `seq 1`; do flash_light ; done ) &
