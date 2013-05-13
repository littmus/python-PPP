class FCS16:

    fcstab = [
        0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf,
        0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
        0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
        0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
        0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd,
        0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
        0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c,
        0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
        0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
        0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
        0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a,
        0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
        0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9,
        0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
        0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
        0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
        0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7,
        0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
        0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036,
        0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
        0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5,
        0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
        0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134,
        0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
        0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3,
        0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb,
        0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232,
        0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a,
        0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
        0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
        0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330,
        0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78,
    ]

    _PPP_INITIAL_FCS16 = 0xffff
    _PPP_GOOD_FCS16 = 0xf0b8

    def __init__(self):
        raise Exception("Do not instantiate FCS class.")

    @classmethod
    def pppfcs16(self, fcs, packet):
        for ch in packet:
            fcs = (fcs >> 8) ^ self.fcstab[(fcs ^ ord(ch)) & 0xff]

        fcs = fcs ^ 0xffff
        fcs = chr(fcs & 0x00ff), chr((fcs >> 8) & 0x00ff)

        return fcs


class HDLCError(Exception):
    def __init__(self, message, packet):
        Exception.__init__(self, message, packet)


from protocol import Protocol


class HDLC:

    _FLAG_SEQUENCE = chr(0x7e)
    _ESCAPE_SEQUENCE = chr(0x7d)
    _ESCAPE_VALUE = 0x20
    _ADDRESS_ALL_STATIONS = chr(0xff)
    _CONTROL_UNNUMBERED_INFO = chr(0x03)

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
        print packet.encode('hex')

        escaped = False
        parsedPacket = []

        for ch in packet:
            if ord(ch) < self._ESCAPE_VALUE:
                continue

            if escaped:
                escaped = False

                if ch is self._FLAG_SEQUENCE:
                    continue

                ch = chr(ord(ch) ^ self._ESCAPE_VALUE)
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
            # case of ['not start with fs, ~~~'], it cannot be a valid packet
            if len(self.inputPacket) == 1:
                self.inputPacket.pop(0)
            raise HDLCError('Starting flag sequence is missing.', packet)

        if not packet.endswith(self._FLAG_SEQUENCE):
            raise HDLCError('Ending flag sequence is missing.', packet)

        # check fcs
        
        # fcs in packet
        fcs_orig = packet[-3:-1].encode('hex')

        # fcs of packet
        fcs_packet = packet[1:-3]
        
        fcs_calc = FCS16.pppfcs16(FCS16._PPP_INITIAL_FCS16, fcs_packet)
        fcs_calc = ''.join(map(lambda c: c.encode('hex'), fcs_calc))

        if fcs_orig != fcs_calc:
            raise HDLCError('Invalid frame check sequence.', packet)
        """
        fcs = FCS16.pppfcs16(FCS16._PPP_INITIAL_FCS16, packet[1:-1])

        if fcs != FCS16._PPP_GOOD_FCS16:
            raise HDLCError('Invalid frame check sequence.', packet)
        """
        # It's valid packet and remove from inputPacket stack
        print 'recv', packet.encode('hex')
        self.inputPacket = []

    def processPacket(self, packet):

        proccessed_packet = []
        packet = ''.join(packet)

        # remove flag sequence, address and control field and fcs
        packet = packet[3:-3]

        protocol_value = int(packet[:2].encode('hex'), 16)
        information = packet[2:]

        # padding?
        protocol = Protocol(protocol_value=protocol_value)
        protocol.sendInfoToProtocol(information)
        protocol.run()
        prtocol_packet = protocol.getInfoFromProtocol()

        proccessed_packet.append(packet)

        return proccessed_packet

    def framePacket(self, packet):

        unframed_packet = []
        framed_packet = []
        packet = ''.join(packet)

        framed_packet.append(self._FLAG_SEQUENCE)

        unframed_packet.append(self._ADDRESS_ALL_STATIONS)
        unframed_packet.append(self._CONTROL_UNNUMBERED_INFO)
        unframed_packet.append(packet)

        unframed_packet = ''.join(unframed_packet)

        fcs = FCS16.pppfcs16(FCS16._PPP_INITIAL_FCS16, unframed_packet)
        fcs = ''.join(map(lambda c: c, fcs))

        unframed_packet += fcs
        for ch in unframed_packet:
            if ord(ch) < self._ESCAPE_VALUE:
                framed_packet.append(self._ESCAPE_SEQUENCE)
                framed_packet.append(chr(ord(ch) ^ self._ESCAPE_VALUE))
            else:
                framed_packet.append(ch)
        
        framed_packet.append(self._FLAG_SEQUENCE)
        framed_packet = ''.join(framed_packet)

        return framed_packet

    def run(self):
        try:
            parsedPacket = self.parsePacket(self.inputPacket)

            self.validatePacket(parsedPacket)

            proccessedPacket = self.processPacket(parsedPacket)

            framedPacket = self.framePacket(proccessedPacket)

            self.outputPacket.append(framedPacket)
        except HDLCError as e:
            print '%s : %s' % (e.args[0], e.args[1].encode('hex'))
            #print ''.join(self.inputPacket).encode('hex')
            #print [ip.encode('hex') for ip in self.inputPacket]
            self.outputPacket.append(-1)
