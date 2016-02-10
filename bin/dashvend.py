#!/usr/bin/env python

import time
import sys

from dashvend.logger import info  # stdout and file logging
from dashvend.addresses import Bip32Chain  # purchase addresses
from dashvend.dashrpc import DashRPC  # local daemon - balances/refunds
from dashvend.dash_ix import InstantX  # dash instantx processing
from dashvend.dash_p2p import DashP2P  # dash network monitor
from dashvend.vend import Vend  # main app and hardware interface

from dashvend.config import MAINNET  # dash network to use
from dashvend.config import VENDING_COST  # dash amount required for purchase


if __name__ == "__main__":
    dashrpc = DashRPC(mainnet=MAINNET)
    dashp2p = DashP2P(mainnet=MAINNET)

    vend = Vend()

    info("connecting to dashd, waiting for masternode and budget sync")
    info("this can take between one to two hours on rpi2")
    dashrpc.connect()
    while(not dashrpc.ready()):
        time.sleep(60)

    bip32 = Bip32Chain(mainnet=MAINNET, dashrpc=dashrpc)

    ix = InstantX()
    vend.set_instantx(ix)  # attach instantx detection
    vend.set_address_chain(bip32)  # attach address chain
    vend.set_product_cost(VENDING_COST)  # set product cost in dash
    vend.set_dashrpc(dashrpc)  # attach local wallet for refunds

    while True:
        dashrpc.connect()
        dashp2p.connect()
        dashp2p.forward(vend.get_listeners())
        info("waiting for dashd to finish synchronizing")
        while(not dashrpc.ready()):
            time.sleep(60)
        vend.set_state(Vend.READY)
        info("*" * 80)
        info(" --> ready. listening to dash %s network." % (MAINNET and 'mainnet' or 'testnet'))
        dashp2p.listen()
        time.sleep(1)
