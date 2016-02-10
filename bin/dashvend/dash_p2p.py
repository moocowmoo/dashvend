# dash p2p traffic monitor
# portions from node.py - Bitcoin P2P network half-a-node
#
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.


from cStringIO import StringIO as BytesIO
import socket
import struct

import dash # noqa - monkeypatches bitcoin lib
import bitcoin
from logging import info
from bitcoin import SelectParams
from bitcoin.messages import msg_version, msg_getdata, msg_pong, MsgSerializable


class DashP2P(object):

    def __init__(self, mainnet=False, host="127.0.0.1", port=None):
        port = port or (mainnet and 9999 or 19999)
        self.mainnet = mainnet
        self.host = host
        self.port = port

        SelectParams(mainnet and 'mainnet' or 'testnet')
        self.netmagic = bitcoin.params

        self.recvbuf = ""
        self.connected = False
        self.route = {}
        pass

    def connect(self):
        info('connecting to dashd')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.send(msg_version().to_bytes())
        info('connected to dashd')
        return self

    def disconnect(self):
        info('disconnecting from dashd')
        self.recvbuf = ""
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except:
            pass

    def process_data(self):
        while True:
            if len(self.recvbuf) < 4:
                return
            if self.recvbuf[:4] != self.netmagic.MESSAGE_START:
                raise ValueError("got garbage %s" % repr(self.recvbuf))
            if len(self.recvbuf) < 4 + 12 + 4 + 4:
                return
            msglen = struct.unpack("<i", self.recvbuf[4+12:4+12+4])[0]
            if len(self.recvbuf) < 4 + 12 + 4 + 4 + msglen:
                return
            message = self.recvbuf[:4+12+4+4+msglen]
            self.recvbuf = self.recvbuf[4+12+4+4+msglen:]
            f = BytesIO(message)
            try:
                msg = MsgSerializable.stream_deserialize(f)
            except ValueError:
                raise ValueError("invalid deserialization %s" % repr(self.recvbuf))  # noqa
            if msg is None:
                return
            self.got_message(msg)

    def got_message(self, msg):
        if msg.command == 'ping':
            pong = msg_pong(nonce=msg.nonce)
            self.sock.send(pong.to_bytes())
        elif msg.command == 'inv':
            for i in msg.inv:
                # transaction/block/txlrequest/txlvote
                if i.type in (1, 2, 4, 5):
                    gd = msg_getdata()
                    gd.inv.append(i)
                    self.sock.send(gd.to_bytes())
        if msg.command in self.route:
            self.route[msg.command](msg)

    def forward(self, args):
        it = iter(args)
        for (msgtype, handler) in zip(it, it):
            self.route[msgtype] = handler

    def unforward(self, args):
        it = iter(args)
        for (msgtype, handler) in zip(it, it):
            if msgtype in self.route:
                del self.route[msgtype]

    def listen(self):
        while True:
            try:
                data = self.sock.recv(8192)
                if len(data) <= 0:
                    raise ValueError
            except (IOError, ValueError):
                self.disconnect()
                return
            self.recvbuf += data
            self.process_data()
