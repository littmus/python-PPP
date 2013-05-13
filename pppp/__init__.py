class PPP:

    _FRAMER = None

    def __init__(self, framer):
        self._FRAMER = framer

    def putPacketToFramer(self, packet):
        self._FRAMER.putPacket(packet)

    def getPacketFromFramer(self):
        return self._FRAMER.getPacket()

    def run(self):
        self._FRAMER.run()
