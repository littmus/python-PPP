from protocol.lcp import LCP
from protocol.ipcp import IPCP


class PPP:

    _FRAMER = None
    _LCP = None
    _IPCP = None
    _OPTIONS = None

    _STATE = 0
    _DEBUG = False

    _SUPPORT_PROTOCOLS = {
        0xc021: 'LCP',
        0x8021: 'IPCP',
    }

    inputPackets = None
    outputPackets = None

    def __init__(self, framer, options):
        self._FRAMER = framer
        self._OPTIONS = options
        self._LCP = LCP(options=self._OPTIONS, ppp=self)
        self._IPCP = IPCP(options=self._OPTIONS, ppp=self)
        self._DEBUG = options['debug']

        self.inputPackets = []
        self.outputPackets = []

    def putPacket(self, packet):
        self.inputPackets.append(packet)

    def getPacket(self):
        return self.outputPackets.pop(0)

    def putPacketToFramer(self, packet):
        self._FRAMER.putPacket(packet)

    def getDataFromFramer(self):
        return self._FRAMER.getData()

    def run(self, income=True):

        no_fs = False
        if income is False and self._STATE == 0:
            protocol = self._LCP
            protocol.run(init=True)
        else:
            if len(self.inputPackets) == 0:
                self.outputPackets = -1
                return -1

            inputPacket = self.inputPackets.pop(0)

            self.putPacketToFramer(inputPacket)
            self._FRAMER.run()

            inputData = self.getDataFromFramer()
            if inputData == -1:
                self.outputPackets.append(inputData)
                return -1

            (protocol_value, info) = inputData
            protocol_name = self._SUPPORT_PROTOCOLS.get(protocol_value)
            if protocol_name is None:
                return -1

            if protocol_name == 'LCP':
                protocol = self._LCP
            elif protocol_name == 'IPCP':
                protocol = self._IPCP
                no_fs = True

            protocol.putInfo(info)
            protocol.run()
            self._STATE = 1

        outputInfo = protocol.getInfo()

        if outputInfo in [-2, -3]:
            self.outputPackets.append(outputInfo)
            return outputInfo

        if outputInfo[2] == chr(0x09):
            no_fs = True
            outputPacket = self._FRAMER.framePacket(outputInfo, no_fs)
            self.outputPackets.append(outputPacket)

            protocol = self._IPCP
            protocol.run(init=True)

            outputInfo = protocol.getInfo()

        outputPacket = self._FRAMER.framePacket(outputInfo, no_fs)

        self.outputPackets.append(outputPacket)
