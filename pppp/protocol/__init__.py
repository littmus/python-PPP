from lcp import LCP
from ipcp import IPCP


class Protocol:

    _PROTOCOL = None
    _PROTOCOL_VALUES = {
        0xc021: LCP(),
        0x8021: IPCP(),
    }

    def __init__(self, protocol_value):
        self._PROTOCOL = self._PROTOCOL_VALUES[protocol_value]
        print self._PROTOCOL._PROTOCOL_NAME

    def sendInfoToProtocol(self, info):
        self._PROTOCOL.putInfo(info)

    def getInfoFromProtocol(self):
        return self._PROTOCOL.getInfo()

    def run(self):
        self._PROTOCOL.run()
