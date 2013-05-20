class FCS16(object):

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
        pass

    @classmethod
    def pppfcs16(self, fcs, packet, formated=False):
        for ch in packet:
            fcs = (fcs >> 8) ^ self.fcstab[(fcs ^ ord(ch)) & 0xff]

        if formated is True:
            fcs = fcs ^ 0xffff
            fcs = chr(fcs & 0x00ff), chr((fcs >> 8) & 0x00ff)

        return fcs

    @classmethod
    def fcsFormat(self, fcs):
        fcs = fcs ^ 0xffff
        fcs = chr(fcs & 0x00ff), chr((fcs >> 8) & 0x00ff)
        fcs = ''.join(map(lambda c: c, fcs))

        return fcs


class HDLCError(Exception):
    def __init__(self, message, packet):
        super(HDLCError, self).__init__(self, message, packet.encode('hex'))


class HDLC(object):

    _FLAG_SEQUENCE = chr(0x7e)
    _ESCAPE_SEQUENCE = chr(0x7d)
    _ESCAPE_VALUE = 0x20
    _ADDRESS_ALL_STATIONS = chr(0xff)
    _CONTROL_UNNUMBERED_INFO = chr(0x03)

    _inputPacket = None
    _outputData = None

    _NO_FS_CASE = [
        chr(0xc0) + chr(0x21) + chr(0x09),
        chr(0xc0) + chr(0x21) + chr(0x0a),
        chr(0x80) + chr(0x21),
    ]

    def __init__(self):
        self.packet = None
        self.inputPacket = []
        self.outputData = []

    def putPacket(self, packet):
        self.inputPacket.append(packet)

    def getData(self):
        return self.outputData.pop(0)

    def unescapePacket(self, packet):

        packet = ''.join(packet)

        escaped = False
        unescapedPacket = []

        for ch in packet:
            #if ord(ch) < self._ESCAPE_VALUE:
            #    continue

            if escaped:
                escaped = False

                if ch is self._FLAG_SEQUENCE:
                    continue

                ch = chr(ord(ch) ^ self._ESCAPE_VALUE)
            elif ch is self._ESCAPE_SEQUENCE:
                escaped = True
                continue

            unescapedPacket.append(ch)

        return unescapedPacket

    def validatePacket_(self, packet):
        packet = ''.join(packet)
        remain_packet = ''

        #print 'validate', packet.encode('hex')

        if len(packet) < 2:
            raise HDLCError('Packet is too short to validate.', packet)

        no_fs = False
        fs_start = packet.startswith(self._FLAG_SEQUENCE)

        if fs_start:
            for case in self._NO_FS_CASE:
                if packet[1:].startswith(case):
                    no_fs = True
                    break

            fs_end = packet.find(self._FLAG_SEQUENCE, 1)
            if fs_end == -1:
                raise HDLCError('Ending flag sequence is missing.', packet)

            if no_fs is True:
                remain_packet = packet[fs_end:]
                packet = packet[1:fs_end]
            else:
                remain_packet = packet[fs_end + 1:]
                packet = packet[:fs_end + 1]
        else:
            for case in self._NO_FS_CASE:
                if packet.startswith(case):
                    no_fs = True
                    break
                if packet[1:].startswith(case):
                    no_fs = True
                    break
                if packet[2:].startswith(case):
                    no_fs = True
                    break
            fs_end = packet.find(self._FLAG_SEQUENCE)
            if fs_end == -1:
                raise HDLCError('Ending flag sequence is missing.', packet)
            
            if no_fs is True:
                remain_packet = packet[fs_end + 1:]
                packet = packet[:fs_end]
            else:
                self.inputPacket = []
                raise HDLCError('Starting flag sequence is missing.', packet)

        fcs = None
        if no_fs is True:
            fcs = FCS16.pppfcs16(FCS16._PPP_INITIAL_FCS16, packet)
        else:
            if len(packet) == 2:
                self.inputPacket = []
                raise HDLCError('Empty Frame', packet)

            address = packet[1]
            if address != self._ADDRESS_ALL_STATIONS:
                raise HDLCError('Invalid address field value.', packet)

            control = packet[2]
            if control != self._CONTROL_UNNUMBERED_INFO:
                raise HDLCError('Invalid control field value.', packet)

            fcs = FCS16.pppfcs16(FCS16._PPP_INITIAL_FCS16, packet[1:-1])

        if fcs != FCS16._PPP_GOOD_FCS16:
            self.inputPacket = []
            raise HDLCError('Invalid frame check sequence value.', packet)

        self.inputPacket = []
        self.inputPacket.append(remain_packet)

        return (packet, no_fs)

    def processPacket(self, packet, no_fs):

        # remove flag sequence, address & control field and fcs
        if no_fs is False:
            packet = packet[3:-3]

        protocol_value = int(packet[:2].encode('hex'), 16)
        information = packet[2:]

        return (protocol_value, information)

    def framePacket(self, packet, no_fs):

        unframed_packet = []
        framed_packet = []

        framed_packet.append(self._FLAG_SEQUENCE)
        if no_fs is False:
            unframed_packet.append(self._ADDRESS_ALL_STATIONS)
            unframed_packet.append(self._CONTROL_UNNUMBERED_INFO)

        unframed_packet.append(packet)
        unframed_packet = ''.join(unframed_packet)

        fcs = FCS16.pppfcs16(FCS16._PPP_INITIAL_FCS16, unframed_packet, True)
        fcs = ''.join(map(lambda c: c, fcs))

        unframed_packet += fcs
        for ch in unframed_packet:
            if ord(ch) < self._ESCAPE_VALUE or ch in [self._FLAG_SEQUENCE, self._ESCAPE_SEQUENCE]:
                framed_packet.append(self._ESCAPE_SEQUENCE)
                framed_packet.append(chr(ord(ch) ^ self._ESCAPE_VALUE))
            else:
                framed_packet.append(ch)

        framed_packet.append(self._FLAG_SEQUENCE)
        framed_packet = ''.join(framed_packet)

        return framed_packet

    def run(self):
        try:
            unescapedPacket = self.unescapePacket(self.inputPacket)

            (validPacket, no_fs) = self.validatePacket_(unescapedPacket)

            protocolData = self.processPacket(validPacket, no_fs)

            self.outputData.append(protocolData)
        except HDLCError as e:
            #print e.args[0]
            self.outputData.append(-1)
