import random
import struct


class LCP:

    _PROTOCOL_VALUE = 0xc021
    _PROTOCOL_NAME = 'LCP'
    _PROTOCOL_STATES = {
        chr(0x01): 'ConfReq',
        chr(0x02): 'ConfAck',
        chr(0x03): 'ConfNak',
        chr(0x04): 'ConfRej',
        chr(0x05): 'TermReq',
        chr(0x06): 'TermAck',
        chr(0x07): 'CodeRej',
        chr(0x08): 'PrtcRej',
        chr(0x09): 'EchoReq',
        chr(0x0a): 'EchoRep',
        chr(0x0b): 'DiscReq',
    }
    _PROTOCOL_CONF_OPTIONS = {
        #chr(0x00): 'RESERVED',
        chr(0x01): 'mru',
        chr(0x02): 'asyncmap',
        #chr(0x03): 'AP',  # Auth protocol
        #chr(0x04): 'QP',  # Quality protocol
        chr(0x05): 'magic',  # Magin number
        chr(0x07): 'pcomp',  # Protocol Field Compression
        chr(0x08): 'accomp',  # Address and Control Field Compression
    }

    inputInfo = None
    outputInfo = None

    _INITIAL_MAGIC = None
    _PREVIOUS_LOCAL_MAGIC = None
    _PREVIOUS_REMOTE_MAGIC = None

    _PPP = None

    DEBUG_PRINT_FORMAT = '%s [%s %s id=0x%x %s]'  # (rcvd, sent) , (protocol), (state), (id), (option)

    def __init__(self, options, ppp):
        self.inputInfo = []
        self.outputInfo = []
        self._OPTIONS = options
        self._PPP = ppp

    def putInfo(self, info):
        self.inputInfo.append(info)

    def getInfo(self):
        return self.outputInfo.pop(0)

    def printDebug(self, direct, info):

        options_str = []
        if info['code'] in [chr(0x01), chr(0x02), chr(0x03), chr(0x04)]:
            for option in info['options']:
                if option['data'] == '':
                    option_str = '<%s>' % self._PROTOCOL_CONF_OPTIONS[option['type']]
                else:
                    option_str = '<%s 0x%00x>' % (self._PROTOCOL_CONF_OPTIONS[option['type']], int(option['data'].encode('hex'), 16))
                options_str.append(option_str)

        elif info['code'] in [chr(0x05), chr(0x06), chr(0x07), chr(0x08)]:
            if info.get('data') is not None:
                options_str.append('"%s"' % info['data'])

        elif info['code'] in [chr(0x09), chr(0x0a), chr(0x0b)]:
            options_str.append('magic=0x%00x' % int(info['magic'].encode('hex'), 16))

            if info.get('data') is not None:
                options_str.append('data=0x%00x' % int(info['data'].encode('hex'), 16))

        options_str = ' '.join(options_str)

        DEBUG_PRINT_DATA = (
            direct,
            self._PROTOCOL_NAME,
            self._PROTOCOL_STATES[info['code']],
            int(info['id'].encode('hex'), 16),
            options_str,
        )

        print self.DEBUG_PRINT_FORMAT % DEBUG_PRINT_DATA

    def getConfigRequest(self):

        if self._INITIAL_MAGIC is None:
            magic = random.randint(long(1), 0xffffffff)
            self._INITIAL_MAGIC = struct.pack('!L', magic)

        info = []
        info.append(struct.pack('!H', self._PROTOCOL_VALUE))
        info.append(chr(0x01))
        info.append(chr(0x01))

        options = []
        options.append(chr(0x02) + chr(0x06) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00))
        options.append(chr(0x05) + chr(0x06) + self._INITIAL_MAGIC)
        self._PREVIOUS_LOCAL_MAGIC = self._INITIAL_MAGIC
        if self._OPTIONS['nopcomp'] is False:
            options.append(chr(0x07) + chr(0x02))
        if self._OPTIONS['noaccomp'] is False:
            options.append(chr(0x08) + chr(0x02))
        options = ''.join(options)

        length = 4 + len(options)

        info.append(struct.pack('!H', length))
        info.append(options)

        info = ''.join(info)

        return info

    def parseInfo(self, info):
        parsed_info = {
            'code': info[0],
            'id': info[1],
            'length': info[2:4],
        }

        if parsed_info['code'] in [chr(0x01), chr(0x02), chr(0x03), chr(0x04)]:
            data = info[4:]
            options = []
            option = {}
            next_length = False
            next_data = False
            for i, ch in enumerate(data):
                if next_length is True:
                    next_length = False

                    option['length'] = ch
                    data_length = int(option['length'].encode('hex'), 16) - 2

                    if data_length == 0:
                        option['data'] = ''
                    else:
                        next_data = True
                        data_end = i + data_length
                        option['data'] = data[i + 1:data_end + 1]

                    options.append(option)
                    option = {}
                    continue

                if next_data is True:
                    if i == data_end:
                        next_data = False
                    continue

                if ch in self._PROTOCOL_CONF_OPTIONS:
                    next_length = True
                    option['type'] = ch

            parsed_info['options'] = options

        elif parsed_info['code'] in [chr(0x05), chr(0x06), chr(0x07), chr(0x08)]:
            if reduce(lambda x,y:(x<<8) + y, struct.unpack('!h', parsed_info['length'])) > 8:
                parsed_info['data'] = info[4:]

        elif parsed_info['code'] in [chr(0x09), chr(0x0a), chr(0x0b)]:
            parsed_info['magic'] = info[4:8]

            if reduce(lambda x,y:(x<<8) + y, struct.unpack('!h', parsed_info['length'])) > 8:
                parsed_info['data'] = info[8:]

        return parsed_info

    def createInfo(self, info):

        # id field changed when contents of the option field changes
        # or valid reply has been received for a previous request
        # when retransmissions, not change
        created_info = []
        magic = random.randint(long(1), 0xffffffff)
        magic = struct.pack('!L', magic)

        created_info.append(struct.pack('!H', self._PROTOCOL_VALUE))

        if info['code'] == chr(0x01):
            self._PPP._STATE = 1
            created_info.append(chr(0x02))
            created_info.append(info['id'])
            created_info.append(info['length'])

            for option in info['options']:
                created_info.append(option['type'])
                created_info.append(option['length'])

                if option['type'] == chr(0x05):
                    self._PREVIOUS_REMOTE_MAGIC = option['data']
                created_info.append(option['data'])

        # send echoreq
        elif info['code'] == chr(0x02):
            created_info.append(chr(0x09) + chr(0x00) + chr(0x00) + chr(0x08))
            created_info.append(magic)
        # send echorep
        elif info['code'] == chr(0x09):
            created_info.append(chr(0x0a) + info['id'] + info['length'])
            created_info.append(self._PREVIOUS_LOCAL_MAGIC)
        elif info['code'] == chr(0x0a):
            return -2
        elif info['code'] == chr(0x05):
            created_info.append(chr(0x06) + info['id'] + chr(0x00) + chr(0x04))

        created_info = ''.join(created_info)

        return created_info

    def run(self, init=False):

        try:
            if init is True and self._PPP._STATE == 0:
                outputInfo = self.getConfigRequest()
            else:
                parsedInfo = self.parseInfo(self.inputInfo.pop(0))

                if self._PPP._DEBUG is True:
                    self.printDebug('rcvd', parsedInfo)
                outputInfo = self.createInfo(parsedInfo)

            if self._PPP._DEBUG is True and outputInfo != -2:
                parsed_info = self.parseInfo(outputInfo[2:])
                self.printDebug('sent', parsed_info)

            self.outputInfo.append(outputInfo)
        except Exception as e:
            #print '%s : %s' % (e.args[0],   e.args[1])
            self.outputInfo.append(-2)
