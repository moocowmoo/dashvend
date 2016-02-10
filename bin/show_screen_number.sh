#!/bin/bash

# FIXME -- move to common include
VEND_DIR=/home/pi/dashvend
BIN_DIR=$VEND_DIR/bin
IMAGEDIR=$VEND_DIR/display/source_images
OUTDIR=/tmp/rendered_images

IMG_BLANK_SCREEN=$IMAGEDIR/_blank_screen-480x800.png
IMG_BG_LOADING_SCREEN=$IMAGEDIR/bg-dash_warp-480x800.png
IMG_BG_PAYMENT_SCREEN=$IMAGEDIR/bg-payment-480x800.png
IMG_BG_REJECTED_SCREEN=$IMAGEDIR/bg-rejected-480x800.png

IMG_QR_OVERLAY=$IMAGEDIR/icon-blue_dash_d-360x360.png

QR_PAYMENT_LABEL=DASH%20N%20DRINK%20www.dashndrink.com

if [ ! -e $OUTDIR ]; then
    mkdir $OUTDIR
fi

function gen_screen_loading(){
    IP=$(/sbin/ifconfig | grep "Bcast" | awk -F":" '{print $2}' | awk -F" " '{print $1}')
    /usr/bin/convert $IMG_BG_LOADING_SCREEN -fill black -pointsize 40 -draw "text 130,740 '$IP'" $OUTDIR/screen-0.png
};

function gen_screen_payment_pending(){

    addinput=$1
    amount=$2

    /usr/bin/qrencode -s 9 -l M -m 0 -o $OUTDIR/qr.png 'dash:'$addinput'?amount='$amount'&label='$QR_PAYMENT_LABEL''
    /usr/bin/composite -blend 100%x100% -gravity center $IMG_QR_OVERLAY $OUTDIR/qr.png $OUTDIR/qrd.png
    /usr/bin/convert $IMG_BG_PAYMENT_SCREEN \
        -fill "rgb(28,117,188)" \
        -pointsize 45 -draw "text 23,80   'SEND $amount'
                             text 23,165  'WITH                   TO'
                             text 23,705  'SELECT BEVERAGE'
                             text 100,760 'AND ENJOY!'" \
        -pointsize 22 -gravity center -draw "text 0,225 '$addinput'" \
        $OUTDIR/payment_screen.png
    /usr/bin/composite -geometry +55+220 $OUTDIR/qrd.png $OUTDIR/payment_screen.png $OUTDIR/screen-1.png
    rm $OUTDIR/{payment_screen,qr,qrd}.png 2>/dev/null
};

function gen_screen_payment_rejected(){
    /usr/bin/composite -geometry +135+450 $IMAGEDIR/instantx40.png $IMG_BG_REJECTED_SCREEN $OUTDIR/payment_rejected.png
    /usr/bin/convert $OUTDIR/payment_rejected.png \
        -fill "rgb(28,117,188)" -pointsize 45 -draw \
            'text 145,155 "PAYMENT" 
             text 125,220 "RETURNED"
             text 55,365 "TRY AGAIN WITH"' \
    $OUTDIR/screen-3.png
    rm $OUTDIR/payment_rejected.png 2>/dev/null
};


case "$1" in

  # show black (blank)
  blank|black)
    $BIN_DIR/show_image $IMG_BLANK_SCREEN
    ;;

  # screen 0 - boot screen -- pending ready
  0)
    gen_screen_loading
    $BIN_DIR/show_image $OUTDIR/screen-0.png
    ;;

  # screen 1 - payment screen -- waiting for dash
  1)
    gen_screen_payment_pending $2 $3
    $BIN_DIR/show_image $OUTDIR/screen-1.png
    ;;

  # screen 2 - payment received -- thank you
  2)
    if [ ! -e $OUTDIR/screen-2.png ] ; then
        cp $IMAGEDIR/screen-2.png $OUTDIR/screen-2.png
    fi
    $BIN_DIR/show_image $OUTDIR/screen-2.png
    ;;

  # screen 3 - payment rejected -- try again
  3)
    if [ ! -e $OUTDIR/screen-3.png ]; then
        gen_screen_payment_rejected
    fi
    $BIN_DIR/show_image $OUTDIR/screen-3.png
    ;;

  # screen 4 - system shutdown
  4)
    # devhak
    if [ ! -e $OUTDIR/screen-4.png ] ; then
        cp $IMAGEDIR/screen-4.png $OUTDIR/screen-4.png
    fi
    $BIN_DIR/show_image $OUTDIR/screen-4.png
    ;;


  *)
    echo "Usage: $0 screen_number" >&2
    exit 3
    ;;

esac
