
import struct

import bitcoin
import bitcoin.core
from bitcoin.core import CTxIn, b2lx
from bitcoin.core.serialize import ser_read, BytesSerializer


class MainParams(bitcoin.core.CoreMainParams):
    MESSAGE_START = b'\xbf\x0c\x6b\xbd'
    DEFAULT_PORT = 9999
    RPC_PORT = 9998
    DNS_SEEDS = ()
    BASE58_PREFIXES = {'PUBKEY_ADDR': 76,
                       'SCRIPT_ADDR': 16,
                       'SECRET_KEY': 204}

bitcoin.params = bitcoin.MainParams = MainParams


class TestNetParams(bitcoin.core.CoreTestNetParams):
    MESSAGE_START = b'\xce\xe2\xca\xff'
    DEFAULT_PORT = 19999
    RPC_PORT = 19998
    DNS_SEEDS = ()
    BASE58_PREFIXES = {'PUBKEY_ADDR': 139,
                       'SCRIPT_ADDR': 19,
                       'SECRET_KEY': 239}

bitcoin.TestNetParams = TestNetParams

import bitcoin.net

bitcoin.net.PROTO_VERSION = 70103


class CInv(bitcoin.net.CInv):
    typemap = {
        0:  "Error",
        1:  "TX",
        2:  "Block",
        3:  "FILTERED_BLOCK",
        4:  "TXLOCK_REQUEST",
        5:  "TXLOCK_VOTE",
        6:  "SPORK",
        7:  "MASTERNODE_WINNER",
        8:  "MASTERNODE_SCANNING_ERROR",
        9:  "BUDGET_VOTE",
        10: "BUDGET_PROPOSAL",
        11: "BUDGET_FINALIZED",
        12: "BUDGET_FINALIZED_VOTE",
        13: "MASTERNODE_QUORUM",
        14: "MASTERNODE_ANNOUNCE",
        15: "MASTERNODE_PING",
        16: "DSTX"}

bitcoin.net.CInv = CInv

import bitcoin.messages


class CTransactionLock(bitcoin.core.ImmutableSerializable):
    """Dash InstantX transaction lock:
        hash, masternode vin, masternode signatures, effective block """
    __slots__ = ['hash', 'vin', 'sig', 'height']

    def __init__(self, hash=b'\x00'*32, vin=CTxIn(), sig=b'\x00'*65, height=0):
        """Create a new transaction lock
        hash is the transaction id being locked
        vin is the masternode funding address
        sig is the masternodes signature for the lock
        height is the block the lock is effective
        If their contents are not already immutable, immutable copies will be
        made.
        """
        if not len(hash) == 32:
            raise ValueError(
                'CTransactionLock: hash must be exactly 32 bytes; got %d bytes' % len(hash)) # noqa
        object.__setattr__(self, 'hash', hash)
        object.__setattr__(self, 'vin', vin)
        if not len(sig) == 65:
            raise ValueError(
                'CTransactionLock: sig must be exactly 65 bytes; got %d bytes' % len(sig)) # noqa
        object.__setattr__(self, 'sig', sig)
        object.__setattr__(self, 'height', height)

    @classmethod
    def stream_deserialize(cls, f):
        hash = ser_read(f, 32)
        vin = CTxIn.stream_deserialize(f)
        sig = BytesSerializer.stream_deserialize(f)
        height = struct.unpack(b"<I", ser_read(f, 4))[0]
        return cls(hash, vin, sig, height)

    def stream_serialize(self, f):
        f.write(self.hash)
        f.write(self.vin.stream_serialize())
        BytesSerializer.stream_serialize(self.sig, f)
        f.write(struct.pack(b"<I", self.height))

    def __repr__(self):
        return 'CTransactionLock(lx(%r), %r, lx(%r), %i)' % (
            b2lx(self.hash), self.vin, b2lx(self.sig), self.height)


class msg_ix(bitcoin.messages.MsgSerializable):
    command = b"ix"

    def __init__(self, protover=bitcoin.net.PROTO_VERSION):
        super(msg_ix, self).__init__(protover)
        self.tx = bitcoin.core.CTransaction()

    @classmethod
    def msg_deser(cls, f, protover=bitcoin.net.PROTO_VERSION):
        c = cls()
        c.tx = bitcoin.core.CTransaction.stream_deserialize(f)
        return c

    def msg_ser(self, f):
        self.tx.stream_serialize(f)

    def __repr__(self):
        return "msg_ix(ix=%s)" % (repr(self.tx))


class msg_txlvote(bitcoin.messages.MsgSerializable):
    command = b"txlvote"

    def __init__(self, protover=bitcoin.net.PROTO_VERSION):
        super(msg_txlvote, self).__init__(protover)
        self.txlvote = CTransactionLock()

    @classmethod
    def msg_deser(cls, f, protover=bitcoin.net.PROTO_VERSION):
        c = cls()
        c.txlvote = CTransactionLock.stream_deserialize(f)
        return c

    def msg_ser(self, f):
        self.txlvote.stream_serialize(f)

    def __repr__(self):
        return "msg_txlvote(tx=%s)" % (repr(self.txlvote))


class msg_ignore():

    @classmethod
    def msg_deser(cls, f, protover=bitcoin.net.PROTO_VERSION):
        return None

bitcoin.messages.msg_txlvote = msg_txlvote
bitcoin.messages.msg_ix = msg_ix
bitcoin.messages.messagemap["txlvote"] = msg_txlvote
bitcoin.messages.messagemap["ix"] = msg_ix

bitcoin.messages.messagemap["ssc"] = msg_ignore
bitcoin.messages.messagemap["dsq"] = msg_ignore
bitcoin.messages.messagemap["dseg"] = msg_ignore
bitcoin.messages.messagemap["getsporks"] = msg_ignore
bitcoin.messages.messagemap["mnget"] = msg_ignore
bitcoin.messages.messagemap["mnvs"] = msg_ignore
