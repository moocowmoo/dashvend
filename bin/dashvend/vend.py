"""
vending app - processing, display, and relay trigger interface
"""

import time
from threading import Timer

from display import Display  # lcd screen for payment screens
from logger import info, warn, debug  # stdout and file logging
from trigger import Trigger  # interface to machine relay

from bitcoinrpc.authproxy import JSONRPCException


class Vend(object):

    # display states (screens)
    STARTUP = 0
    READY = 1
    SALE = 2
    TXREFUND = 3
    SHUTDOWN = 4

    def __init__(self):
        """ connect hardware, initialize state dir """
        self.trigger = Trigger()
        self.display = Display()
        self.current_address = None
        self.cost = 0
        self.set_state(Vend.STARTUP)

    def get_listeners(self):
        return ('tx', self.ix.recv_tx,
                'ix', self.ix.recv_ix,
                'txlvote', self.ix.recv_votes,
                'block', self.recv_block)

    def set_instantx(self, ix):
        ix.set_vend(self)
        self.ix = ix

    def set_dashrpc(self, dashrpc):
        self.dashrpc = dashrpc

    # payment processing

    def set_address_chain(self, bip32):
        """ attach pycoin key instance """
        self.bip32 = bip32
        self.get_next_address()

    def get_next_address(self, increment=False):
        """ payment address to monitor """
        self.current_address = self.bip32.get_next_address(increment)
        self.ix.set_watch_address(self.current_address)

    def set_product_cost(self, cost):
        """ set required float value to trigger sale """
        # convert to duffs
        self.cost = int(cost * 1e8)

    # vending processing

    def trigger_sale(self):
        self.set_state(Vend.SALE)
        self.trigger.trigger()
        Timer(15, lambda: self.set_state(Vend.READY), ()).start()

    def show_txrefund(self):
        self.set_state(Vend.TXREFUND)
        Timer(10, lambda: self.set_state(Vend.READY), ()).start()

    def set_state(self, state):
        self.state = state
        self.display.show_screen_number(
            self.state, self.current_address, float(self.cost / 1e8))

    # refunds processing

    def recv_block(self, msg):
        """ process tx refunds at each new block """
        info(" --> new block: %s" % self.dashrpc._proxy.getblockcount())
        self._process_refunds(msg)

    def _process_refunds(self, msg):  # noqa
        for txid in self.ix.mempool:
            # TODO check block contains tx payment to be refunded
            if 'refunded' in self.ix.mempool[txid]:
                continue
            if 'processed' in self.ix.mempool[txid]:
                if self.ix.mempool[txid]['processed']['refund'] > 0:
                    p = self.ix.mempool[txid]['processed']
                    refund_addr = self.select_return_address(txid)
                    info('  --> refunding %s to %s' % (p['refund'], refund_addr))  # noqa
                    self.sendtoaddress(refund_addr, p['refund'])
                    p['refunded'] = True
        for txid in self.ix.mempool.keys():
            # delete completed (sold/refunded) mempool entries
            if 'processed' in self.ix.mempool[txid]:
                p = self.ix.mempool[txid]['processed']
                if ('refunded' in p or 'sold' in p):
                    label = ' + '.join(
                        [i for i in (
                            'sale' in p and 'SALE',
                            'refunded' in p and 'REFUND'
                            ) if i])
                    debug("  --> deleting processed mempool txid: %s -- %s" % (txid, label))  # noqa
                    del self.ix.mempool[txid]
            # delete non-target cached votes after 1 minute
            elif 'recv_time' in self.ix.mempool[txid]:
                # keep pending refunds in queue (insufficient funds)
                if 'processed' in self.ix.mempool[txid]:
                    if ('refund' in self.ix.mempool[txid]['processed'] and
                            self.ix.mempool[txid]['processed']['refund'] > 0):
                        continue
                if int(time.time()) - self.ix.mempool[txid]['recv_time'] > 60:
                        debug("  --> deleting stale mempool txid: %s" % txid)
                        del self.ix.mempool[txid]

    def sendtoaddress(self, addr, amount):
        p = self.dashrpc._proxy
        try:
            p.sendtoaddress(addr, amount)
        except JSONRPCException:
            warn("**********************************************************")
            warn("INSUFFICIENT FUNDS TO PROCESS REFUND/BOUNCE FOR")
            warn("    %s to %s " % (amount, addr))
            warn("    wallet balance: %s" % (p.getbalance()))
            warn("**********************************************************")

    def get_txn(self, txid):
        p = self.dashrpc._proxy
        return p.decoderawtransaction(p.getrawtransaction(txid))

    def select_return_address(self, txid):
        prevout = self.get_txn(txid)[u'vin'][0]
        source = self.get_txn(prevout[u'txid'])[u'vout']
        return source[prevout[u'vout']][u'scriptPubKey'][u'addresses'][0]
