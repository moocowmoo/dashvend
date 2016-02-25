#!/bin/bash

# relay pinouts are inverted
ON=0
OFF=1

# RPI2 pinouts
PINOUT_LIGHT=5
PINOUT_RELEASE=6

# ODROID pinouts
if [ $(grep ODROID /proc/cpuinfo | wc -l ) -gt 0 ];then
    PINOUT_LIGHT=173
    PINOUT_RELEASE=171
fi


DEV=/sys/class/gpio
LIGHT=$DEV/gpio${PINOUT_LIGHT}
RELAY=$DEV/gpio${PINOUT_RELEASE}

function flash_light(){
    echo $ON  > $LIGHT/value ; sleep .5 ;
    echo $OFF > $LIGHT/value ; sleep .5 ;
};

# initialize gpio directories
if [ ! -e $DEV/gpio${PINOUT_LIGHT} ] ; then echo ${PINOUT_LIGHT} > $DEV/export ; fi
if [ ! -e $DEV/gpio${PINOUT_RELEASE} ] ; then echo ${PINOUT_RELEASE} > $DEV/export ; fi

# initialize pin outputs
echo out > $RELAY/direction
echo out > $LIGHT/direction

# toggle dispensing relay
( echo $ON > $RELAY/value ; sleep .3 ; echo $OFF > $RELAY/value) &

# flash sign lights
( for x in `seq 1`; do flash_light ; done ) &
