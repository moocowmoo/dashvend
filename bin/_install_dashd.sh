#!/bin/bash

echo "installing dashd"

if [ -e ~/.dash/dash.conf ]; then
    exit 0
fi

mkdir -p ~/.dash/testnet/testnet3
cp -f bin/.dash.conf.template ~/.dash
cd ~/.dash
touch dashd.pid testnet/testnet3/dashd.pid
wget https://www.dash.org/binaries/dash-0.12.0.56-RPi2.tar.gz
tar zxvf dash-0.12.0.56-RPi2.tar.gz
ln -s dash-0.12.0/bin/dash-cli .
ln -s dash-0.12.0/bin/dashd .
export PATH=~/.dash:$PATH
echo 'export PATH=~/.dash:$PATH' >> ~/.bashrc

wget https://raw.githubusercontent.com/UdjinM6/dash-bootstrap/master/links.md -O links.md
MAINNET_BOOTSTRAP_FILE=$(head -1 links.md | awk '{print $11}' | sed 's/.*\(http.*\.zip\).*/\1/')
wget $MAINNET_BOOTSTRAP_FILE
unzip ${MAINNET_BOOTSTRAP_FILE##*/}
rm links.md bootstrap.dat*.zip

cd testnet/testnet3
wget https://raw.githubusercontent.com/UdjinM6/dash-bootstrap/master/linksTestnet.md -O linksTestnet.md
TESTNET_BOOTSTRAP_FILE=$(head -1 linksTestnet.md | awk '{print $11}' | sed 's/.*\(http.*\.zip\).*/\1/')
wget $TESTNET_BOOTSTRAP_FILE
unzip ${TESTNET_BOOTSTRAP_FILE##*/}
rm linksTestnet.md bootstrap.dat*.zip

# build confs
function render_conf() {
    RPCUSER=`echo $(dd if=/dev/urandom bs=128 count=1 2>/dev/null) | sha256sum | awk '{print $1}'`
    RPCPASS=`echo $(dd if=/dev/urandom bs=128 count=1 2>/dev/null) | sha256sum | awk '{print $1}'`
    while read; do
        eval echo "$REPLY"
    done < .dash.conf.template > $1
}
render_conf dash.conf
render_conf testnet/dash.conf
echo "testnet=1" >> testnet/dash.conf
dashd
dashd -datadir=testnet
