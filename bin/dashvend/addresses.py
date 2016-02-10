"""
bip32 address management
"""
import os

from config import DASHVEND_DIR, BIP32_MAINNET_SEED, BIP32_TESTNET_SEED
from logger import info
from pycoin.key import Key


class Bip32Chain(object):

    def __init__(self, mainnet, dashrpc):
        self.dashrpc = dashrpc
        self.mainnet = mainnet
        self._init_state_dir(os.path.join(DASHVEND_DIR, 'state'))
        self.key = Key.from_text(
            mainnet and BIP32_MAINNET_SEED or BIP32_TESTNET_SEED)
        self._init_next_address()

    def _init_state_dir(self, statedir):
        """ initialize state directory, content """
        self.statedir = statedir
        if not os.path.isdir(statedir):
            os.makedirs(statedir)
        index_filename = (
            'bip32_index' + (self.mainnet and '-mainnet' or '-testnet'))
        self.bip32_index_file = os.path.join(statedir, index_filename)
        if not os.path.isfile(self.bip32_index_file):
            with open(self.bip32_index_file, 'w') as f:
                f.write('0')

    def _index_state(self, index=None):
        """ getset bip32 index value on disk """
        with open(self.bip32_index_file, 'r+') as f:
            if index is not None:
                f.write(str(index))
                f.seek(0)
            return f.read()

    def get_bip32_address_info(self, index):
        """ get bip32 address and received amount """
        addr = self.key.subkey(index).address(use_uncompressed=False)
        return {
            "index": index,
            "addr": addr,
            "received": float(
                self.dashrpc._proxy.getreceivedbyaddress(addr))
        }

    def _init_next_address(self, increment=False):
        """ find next unused bip32 address, update state """
        r = self.dashrpc._proxy
        index = int(self._index_state())
        if increment:
            index += 1
        unused_found = False
        while (not unused_found):
            addr = self.get_bip32_address_info(index)
            if addr['received'] > 0:
                index += 1
                continue
            unused_found = True
        r.importaddress(addr['addr'], 'bip-'+str(index), False)
        self._index_state(index)
        self.next_address = addr

    def get_next_address(self, increment=False):
        self._init_next_address(increment)
        info("--> new active payment address: %s" % self.next_address['addr'])
        return self.next_address['addr']
