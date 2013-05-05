class HDLC:

    def __init__(self, frame):
        self.frame = frame

    HDLC_FLAG_SEQUENCE = 0x7e
    HDLC_ADDRESS = 0xff
    HDLC_CONTROL = 0x03

    def parseFrame(self):

        frame = self.frame

        return map(lambda x, y: x + y, frame[::2], frame[1::2])
