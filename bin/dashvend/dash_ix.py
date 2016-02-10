"""
InstantX detection
"""

import time

from config import IX_LOCK_TRESHOLD
from logger import info
from bitcoin.core import b2lx
from bitcoin.wallet import P2PKHBitcoinAddress, CBitcoinAddressError


def JSONtoAmount(value):
    return long(round(value * 1e8))


def AmountToJSON(amount):
    return float(amount / 1e8)


class InstantX(object):

    def __init__(self):
        self.mempool = {}
        self.vend = None
        self.dashrpc = None

    def set_vend(self, vend):
        """ attach vending interface """
        self.vend = vend

    def set_watch_address(self, current_address):
        self.current_address = current_address

    def recv_tx(self, msg):
        """ tx handler """
        txid = b2lx(msg.tx.GetHash())
        info("   tx: %s" % txid)
        if self._find_payment(msg, txid, 'tx'):
            # refund at next block
            self.vend.show_txrefund()

    def recv_ix(self, msg):
        """ ix handler """
        txid = b2lx(msg.tx.GetHash())
        info("   IX: %s" % txid)
        if self._find_payment(msg, txid, 'ix'):
            p = self.mempool[txid]['processed']
            info("    --> address match! %s received %s -- %s " % (
                p['addr'], float(p['value']/1e8), p['sale'] and 'SALE!' or ''))
            if self.mempool[txid]['processed']['sale']:
                self._check_ix_threshold(txid)

    def recv_votes(self, msg):
        """ vote (transaction lock) collation """
        txid = b2lx(msg.txlvote.hash)
        vin = (b2lx(msg.txlvote.vin.prevout.hash) + "-" +
               str(msg.txlvote.vin.prevout.n))
        if txid not in self.mempool:
            self.mempool[txid] = {}
        if 'recv_time' not in self.mempool[txid]:
            self.mempool[txid]['recv_time'] = int(time.time())
        if 'locks' not in self.mempool[txid]:
            self.mempool[txid]['locks'] = set()
        self.mempool[txid]['locks'].add(vin)
        # only print locks for target addresses
        if 'processed' in self.mempool[txid]:
            info("    LOCK: %s from %s" % (txid, vin))
        self._check_ix_threshold(txid)

    def _find_payment(self, msg, txid, txtype):
        """ search ix/tx for transaction matching current address """
        addr = None
        value = 0
        refund = 0
        for vout in msg.tx.vout:
            try:
                addr = str(P2PKHBitcoinAddress.from_scriptPubKey(
                    vout.scriptPubKey))
            except CBitcoinAddressError:
                continue
            if addr == self.current_address:
                value = int(vout.nValue)
                break
        # current address received something
        if addr and value:
            # calculate under/overpay refund
            if value < self.vend.cost:
                refund = AmountToJSON(value)
            elif value > self.vend.cost:
                refund = AmountToJSON(value - self.vend.cost)
            if txid not in self.mempool:
                self.mempool[txid] = {}
            # set transaction type, tx refund
            self.mempool[txid][txtype] = True
            if txtype == 'tx':
                tx = self.mempool[txid]['processed']
                tx['refund'] = AmountToJSON(tx['value'])
            self.mempool[txid]['processed'] = {
                "addr": addr,
                "value": value,
                "refund": refund,
                "sale": (value >= self.vend.cost and True or False)
            }
            self.vend.get_next_address(increment=True)
            return True

    def _check_ix_threshold(self, txid):
        """ check for ix + sufficient locks """
        if txid in self.mempool:
            if ('ix' in self.mempool[txid] and 'locks' in self.mempool[txid]):
                if 'sold' in self.mempool[txid]:
                    return
                if len(self.mempool[txid]['locks']) >= IX_LOCK_TRESHOLD:
                    if self.mempool[txid]['processed']['sale']:
                        self.vend.trigger_sale()
                        self.mempool[txid]['sold'] = True
