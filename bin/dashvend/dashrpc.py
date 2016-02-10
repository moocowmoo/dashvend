import os
import socket
import subprocess
from collections import deque
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException, httplib
from logger import info


def simplemovingaverage(period):
    assert period == int(period) and period > 0, "Period must be an integer >0"
    val = {"summ": 0.0, "n": 0.0}
    values = deque([0.0] * period)

    def sma(x):
        x = float(x)
        values.append(x)
        val['summ'] += x - values.popleft()
        val['n'] = min(val['n']+1, period)
        return val['summ'] / val['n']
    return sma


class DashRPC(object):

    def __init__(self,
                 mainnet=False,
                 conf=None
                 ):
        self.mainnet = mainnet
        self.datadir = os.path.join(os.environ['HOME'],
                                    '.dash', (not mainnet and 'testnet'))
        self.conffile = conf and conf or os.path.join(self.datadir, 'dash.conf')
        self.config = {}
        self.cpu_pct = simplemovingaverage(5)
        self._parse_conffile()
        if 'rpcbind' not in self.config:
            self.config['rpcbind'] = '127.0.0.1'
        if 'rpcport' not in self.config:
            self.config['rpcport'] = mainnet and 9998 or 19998

    def _parse_conffile(self):
        with open(self.conffile, 'r') as f:
            lines = list(
                line
                for line in
                (l.strip() for l in f)
                if line and not line.startswith('#'))
            for line in lines:
                conf = line.split('=')
                self.config[conf[0].strip()] = conf[1].strip()

    def connect(self):
        protocol = 'http'
        if ('rpcssl' in self.config and
                bool(self.config['rpcssl']) and
                int(self.config['rpcssl']) > 0):
            protocol = 'https'
        serverURL = protocol + '://' + self.config['rpcuser'] + ':' + \
            self.config['rpcpassword'] + '@' + str(self.config['rpcbind']) + \
            ':' + str(self.config['rpcport'])
        self._proxy = AuthServiceProxy(serverURL)
        return self._proxy

    def get_cpu_average(self):
        pidfile = self.mainnet and '.dash/dashd.pid' or '.dash/testnet/testnet3/dashd.pid'  # noqa
        cmd = "top -p `cat $HOME/%s` -n1 | awk '/ dashd /{print $10}'" % pidfile
        cpu = subprocess.check_output(cmd, shell=True).rstrip('\n') or 100
        return self.cpu_pct(cpu)

    def ready(self):
        self.responding = False
        self.synchronised = False

        self.get_cpu_average()

        try:
            self._proxy.getinfo()
            self.responding = True
        except (ValueError, socket.error, httplib.CannotSendRequest) as e:
            # print "daemon offline"
            pass
        except JSONRPCException as e:
            # "loading block index"
            # print str(e.error['message'])
            pass

        try:
            resp = self._proxy.masternode('debug')
            if 'Node just started' not in resp:
                self.synchronised = True
        except (ValueError, socket.error, httplib.CannotSendRequest) as e:
            # print "daemon offline"
            pass
        except JSONRPCException as e:
            resp = str(e.error['message'])
            if 'masternode' in resp:
                if self.get_cpu_average() < 50:
                    self.synchronised = True

        logmsg = self.responding and 'responding, ' or 'not responding, '
        logmsg += self.synchronised and 'synchronised, ' or 'not synchronised, '
        logmsg += 'cpu: ' + "{0:.2f}".format(self.get_cpu_average())
        info(logmsg)

        return (self.responding and self.synchronised)

# doesn't work due to
#            name = "%s.%s" % (self.__service_name, name)
#        return AuthServiceProxy(self.__service_url, name, connection=self.__conn)  # noqa
#    def __getattr__(self, attr):
#        if getattr(self._proxy, attr):
#            getattr(self._proxy, attr)()
#        else:
#            raise AttributeError
