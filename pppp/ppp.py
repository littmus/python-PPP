class PPP:

    framer = None
    protocol = None

    def __init__(self, framer):
        self.framer = framer

    def putPacketToFramer(self, packet):
        self.framer.putPacket(packet)

    def getPacketFromFramer(self):
        return self.framer.getPacket()

    def run(self):
        self.framer.run()
