# dashvend

Example system for processing Dash InstantX payments

This repo contains everything needed to recreate the Miami "dash'n'drink" soda
machine InstantX tech demo.

# overview

Dashvend is a network-driven python script which:
 - generates payment addresses
 - masquerades as a local dashd peer (port 9999 communication)
 - watches for transactions on the dash network to the next payment address
 - refunds non-InstantX transactions and over/underpaid InstantX transactions
 - counts masternode locks for passing transactions
 - triggers two relays (sign light, product release) when the lock count meets a configurable threshold

## processing overview

    network traffic -> dashd -> dash_p2p.py -> vend.py -> dash_ix.py -> vend.py -> screen/relay

All signature validation of locks is performed by dashd.

# component overview
## dashvend

    bin/dashvend.py          - top-level script
    bin/dashvend/config.py   - system configuration variables
    bin/dashvend/dash_ix.py  - InstantX processing
    bin/dashvend/dash_p2p.py - dash node peer connection
    bin/dashvend/dash.py     - python-bitcoinlib compatibility monkey-patch
    bin/dashvend/dashrpc.py  - dashd rpc communication (refunds, balances)
    bin/dashvend/display.py  - display controller (setuid bash wrapper)
    bin/dashvend/trigger.py  - relay controller (setuid bash wrapper)
    bin/dashvend/vend.py     - main application

## helpers
    bin/_install_dashd.sh         - fresh install - Makefile utility
    /etc/init.d/dashvend          - starts dashd/dashvend on boot/shutdown
    bin/_dashvend_control.sh      - called by above, starts/stops screen processes
    bin/dashvend_screens.screenrc - gnu screen config file for above
    bin/trigger_relay             - setuid script, calls .sh file below
    bin/trigger_relay.sh          - run as root, triggers gpio pins
    display/show_image            - setuid script, calls .sh file below
    display/show_image.sh         - run as root, invokes fbi to display image
    display/show_screen_number.sh - screen image builder, uses imagemagic
    display/source_images/        - source images for above


# boot sequence

After running 'make init', on boot, /etc/init.d/dashvend will (through
bin/_dashvend_control.sh) start a screen session named 'dashvend_screens' with
two screens running:
- dashd (printtoconsole=1) (no debug.log writing to sd card)
- bin/dashvend.py (the main application)

Once the cpu load settles to under 50%, (this can take a while on a pi, see
limitations below) the vending app indicates it is ready to process payments.

# rpi2 limitations

Slow disk I/O is a major contributor to slow rpi2 startup times.
Using a class 10 SD card, after booting, dashd can take up to two hours
(sometimes longer) to fully synchronize with the network and be ready to accept
InstantX transactions. Mounting a USB drive and symlinking the .dash directory
can bring startup times down to around an hour.

# install

For relay and 480x800 lcd display support, you'll need to build or download the
raspberry pi 2 image shown below.

Once you have a base image, run the following to install all the dashvend dependencies:

    git clone https://github.com/moocowmoo/dashvend.git
    make
    # after entering your sudo password, allow several hours/overnight for
    # dashd to finish bootstrapping the blockchain

## dedicated install

To install the boot/shutdown init scripts, do:

    make init

# dedicated raspberry pi 2 install

## hardware

To build your own dash'n'drink implementation you'll need:
- a raspberry pi 2
- an hdmi monitor and attached keyboard (to build the image)
- a 480x800 pixel hdmi lcd screen - the soda machine used http://goo.gl/rcBJD6
- any 5v dual relay board attached to (gpio 5 (sign light) and 6 (soda release), pins 29 and 31)

A 2 amp power supply is recommended for stability.

## downloading the base raspberry pi 2 image

If you want to save time, and have the 480x800 lcd screen attached, you can
skip building the base image by downloading it from:
    https://github.com/moocowmoo/dashvend_rpi2_base_image
If you don't have the 480x800 screen, you can ssh into the machine (user pi,
password raspberry) over ethernet and comment out the lcd-specific entries in
/boot/config.txt (see section below) and reboot to use a hdmi monitor.

## building the base image

Write image 'raspbian jessie lite' found on https://www.raspberrypi.org/downloads/raspbian/ to an sd card

    # be careful with this command, you can destroy data if you don't set the
    # dd target (sd card location) correctly
    unzip -qc 2016-02-03-raspbian-jessie-lite.zip 2016-02-03-raspbian-jessie-lite.img | sudo dd of=/dev/sdb

 - attach keyboard, hdmi monitor, ethernet, sd card
 - boot
 - login as pi, password raspberry
 - change pi password
 - resize partition with 'raspi-config'
 - reboot
 - configure /boot/config.txt and /boot/cmdline.txt for 480x800 screen and overclocking (see below)
 - connect lcd
 - reboot
 - sudo apt-get update
 - sudo apt-get upgrade
 - sudo apt-get install git
 - configure wifi - https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md
 - ssh in through wifi
 - disconnect ethernet
 - reboot
 - ssh in through wifi
 - install dashvend

## 480x800 hdmi lcd screen configuration
### /boot/config.txt

    disable_overscan=1
    hdmi_force_hotplug=1
    hdmi_group=2
    hdmi_mode=87
    hdmi_cvt 800 480 60 6 0 0 0
    display_rotate=3
    gpu_mem=16
    dtparam=spi=off

### /boot/cmdline.txt
    add consoleblank=0
    for example:
    dwc_otg.lpm_enable=0 console=ttyAMA0,115200 console=tty1 consoleblank=0 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait

### /etc/kbd/config
    BLANK_TIME=0
    POWERDOWN_TIME=0
    BLANK_DPMS=on

## optional overclocking (recommended)
### /boot/config.txt
    arm_freq=1100  # with heatsink. works best @ 1100, but not all rpi2's can do it
    sdram_freq=500
    core_freq=500
    over_voltage=2
    temp_limit=80

## post-install setup

### configuration: bin/dashvend/config.py
Before launching dashvend, you need to configure your payment address seed.
See instructions in bin/dashvend/config.py

### refunds
You will need to fund the local wallet to process refunds. do:

    dash-cli getnewaddress

and send some dash to it.

If the local wallet has insufficient funds to process a refund/bounce, it will
write an error in the log file until funded.
