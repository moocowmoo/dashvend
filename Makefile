
default: deps repos dashd setuids

deps:
	sudo apt-get -y install vim git imagemagick fbi qrencode curl unzip screen python-setuptools

repos:
	mkdir -p repos
	cd repos; \
	git clone https://github.com/jgarzik/python-bitcoinrpc.git; \
	git clone https://github.com/richardkiss/pycoin.git; \
	git clone https://github.com/petertodd/python-bitcoinlib.git; \
	ln -f -s ../repos/python-bitcoinrpc/bitcoinrpc ../bin/bitcoinrpc; \
	ln -f -s ../repos/pycoin/pycoin ../bin/pycoin; \
	ln -f -s ../repos/python-bitcoinlib/bitcoin ../bin/bitcoin; \
    cd pycoin; sudo python setup.py install

dashd:
	bin/_install_dashd.sh

setuids:
	cp src/show_image.c bin/show_image.c
	cp src/trigger_relay.c bin/trigger_relay.c
	sed -i 's|DASHVEND_DIRECTORY|$(PWD)|' bin/show_image.c bin/trigger_relay.c
	gcc bin/show_image.c -o bin/show_image
	gcc bin/trigger_relay.c -o bin/trigger_relay
	sudo chown root:root bin/show_image
	sudo chmod 4755 bin/show_image
	sudo chown root:root bin/trigger_relay
	sudo chmod 4755 bin/trigger_relay

init:
	sudo cp bin/.init.d.dashvend /etc/init.d/dashvend
	sudo update-rc.d dashvend defaults
	sudo update-rc.d dashvend enable
	@# TODO bip generation

clean:
	find . -type f -name '*.pyc' -exec rm {} \;
	find . -type f -name '*.o' -exec rm {} \;
	sudo rm -rf repos bin/bitcoin bin/pycoin bin/bitcoinrpc bin/trigger_relay bin/show_image
