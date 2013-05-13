class IPCP:

    _PROTOCOL_VALUE = 0x8021
    _PROTOCOL_NAME = 'IPCP'

    inputInfo = None
    outputInfo = None

    DEBIG_PRINT_FORMAT = '%s [%s %s id=%x %s]'  # (rcvd, sent) , (protocol), (state), (id), (option)

    def __init__(self):
        self.inputInfo = []
        self.outputInfo = []

    def putInfo(self, info):
        self.inputInfo.append(info)

    def getInfo(self):
        return self.outputInfo.pop(0)

    def parseInfo(self, info):
        pass

    def validateInfo(self, info):
        pass

    def processInfo(self, info):
        pass

    def createInfo(self, info):
        pass

    def run(self):
        info = ''.join(self.inputInfo)
        self.outputInfo.append(info)
        pass