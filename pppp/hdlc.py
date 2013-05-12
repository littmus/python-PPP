class FCS16:

    def __init__(self):
        raise Exception("Do not instantiate FCS class.")

# CRC must not be escaped


class HDLCError(Exception):
    def __init__(self, message, packet):
        Exception.__init__(self, message, packet)


class HDLC:

    _FLAG_SEQUENCE = chr(0x7e)
    _ESCAPE_SEQUENCE = chr(0x7d)
    _ADDRESS_ALL_STATIONS = chr(0xff)
    _CONTROL_UNNUMBERED_INFO = chr(0x03)

    #_PROTOCOL_LCP = 

    inputPacket = None
    outputPacket = None

    def __init__(self):
        self.packet = None
        self.inputPacket = []
        self.outputPacket = []

    def putPacket(self, packet):
        self.inputPacket.append(packet)

    def getPacket(self):
        return self.outputPacket.pop(0)

    def parsePacket(self, packet):

        packet = ''.join(packet)

        escaped = False
        parsedPacket = []

        for ch in packet:
            if ord(ch) < 0x20:
                continue

            if escaped:
                escaped = False

                if ch is self._FLAG_SEQUENCE:
                    continue

                ch = chr(ord(ch) ^ 0x20)
            elif ch is self._ESCAPE_SEQUENCE:
                escaped = True
                continue

            parsedPacket.append(ch)

        return parsedPacket

    def validatePacket(self, packet):

        packet = ''.join(packet)

        if len(packet) < 2:
            raise HDLCError('Invalid packet length.', packet)

        if not packet.startswith(self._FLAG_SEQUENCE):
            if len(self.inputPacket) == 1:
                self.inputPacket.pop(0)
            raise HDLCError('Starting flag sequence is missing.', packet)

        if not packet.endswith(self._FLAG_SEQUENCE):
            raise HDLCError('Ending flag sequence is missing.', packet)

        # check CRC

        # its valid packet and remove from inputPacket stack
        print 'recv', packet.encode('hex')
        self.inputPacket = []

    def processPacket(self, packet):

        proccessed_packet = []
        packet = ''.join(packet)

        # remove flag sequence
        packet = packet[1:-1]

        # remove address and control field
        packet = packet[2:]

        proccessed_packet.append(packet)
        return proccessed_packet

    def framePacket(self, packet):

        framed_packet = []
        unframed_packet = []
        packet = ''.join(packet)

        unframed_packet.append(self._FLAG_SEQUENCE)
        unframed_packet.append(self._ADDRESS_ALL_STATIONS)
        unframed_packet.append(self._CONTROL_UNNUMBERED_INFO)
        unframed_packet.append(packet)
        #unframed_packet.append(CRC)
        unframed_packet.append(self._FLAG_SEQUENCE)

        unframed_packet = ''.join(unframed_packet)
        for ch in unframed_packet:
            if ord(ch) < 0x20:
                framed_packet.append(self._ESCAPE_SEQUENCE)
                framed_packet.append(chr(ord(ch) ^ 0x20))
            else:
                framed_packet.append(ch)

        return ''.join(framed_packet)

    def run(self):
        try:
            parsedPacket = self.parsePacket(self.inputPacket)

            self.validatePacket(parsedPacket)

            proccessedPacket = self.processPacket(parsedPacket)

            self.outputPacket.append(self.framePacket(proccessedPacket))
        except HDLCError as e:
            print '%s : %s' % (e.args[0], e.args[1].encode('hex'))
            print [ip.encode('hex') for ip in self.inputPacket]
            self.outputPacket.append(-1)
