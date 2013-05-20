import struct
import subprocess


class IPCP:

    _PROTOCOL_VALUE = 0x8021
    _PROTOCOL_NAME = 'IPCP'
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
        #chr(0x01): 'ip-address',
        chr(0x02): 'compress',
        chr(0x03): 'addr',
    }

    inputInfo = None
    outputInfo = None

    _SCRIPT_IP_UP = '/etc/ppp/ip-up'
    _SCRIPT_IP_DOWN = '/etc/ppp/ip-down'

    _PPP = None
    _STATUS = None

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
                    if option['type'] == chr(0x02):
                        data = option['data'].encode('hex')
                        (max_slot_id, comp_slot_id) = (data[4:6], data[6:])
                        max_slot_id = ''.join(max_slot_id)
                        comp_slot_id = ''.join(comp_slot_id)

                        option_str = '<%s VJ %s %s>' % (self._PROTOCOL_CONF_OPTIONS[option['type']], max_slot_id, comp_slot_id)
                    elif option['type'] == chr(0x03):
                        ip = option['data'].encode('hex')
                        ip = zip(ip[::2], ip[1::2])
                        ip = map(lambda c: str(int(''.join(c), 16)), ip)
                        ip = '.'.join(ip)
                        option_str = '<%s %s>' % (self._PROTOCOL_CONF_OPTIONS[option['type']], ip)
                    else:
                        option_str = '<%s 0x%s>' % (self._PROTOCOL_CONF_OPTIONS[option['type']], option['data'].encode('hex'))
                options_str.append(option_str)

        elif info['code'] in [chr(0x05), chr(0x06), chr(0x07), chr(0x08)]:
            pass

        elif info['code'] in [chr(0x09), chr(0x0a), chr(0x0b)]:
            options_str.append('magic=0x%s' % info['magic'].encode('hex'))

            if info.get('data') is not None:
                options_str.append('data=0x%s' % info['data'].encode('hex'))

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

        info = []
        info.append(struct.pack('!H', self._PROTOCOL_VALUE))
        info.append(chr(0x01))
        info.append(chr(0x01))
        info.append(chr(0x00) + chr(0x10))
        info.append(chr(0x02) + chr(0x06) + chr(0x00) + chr(0x2d) + chr(0x0f) + chr(0x01))
        info.append(chr(0x03) + chr(0x06))

        local_ip = self._OPTIONS['local_ip']
        local_ip = map(lambda x: chr(int(x)), local_ip.split('.'))
        local_ip = ''.join(local_ip)
        info.append(local_ip)

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
            pass

        elif parsed_info['code'] in [chr(0x09), chr(0x0a), chr(0x0b)]:
            parsed_info['magic'] = info[4:8]

            if reduce(lambda x,y:(x<<8) + y, struct.unpack('!h', parsed_info['length'])) > 8:
                parsed_info['data'] = info[8:]

        return parsed_info

    def createInfo(self, info):

        created_info = []

        created_info.append(struct.pack('!H', self._PROTOCOL_VALUE))

        if info['code'] == chr(0x01):
            created_info.append(chr(0x02))
            created_info.append(info['id'])
            created_info.append(info['length'])

            for option in info['options']:
                created_info.append(option['type'])
                created_info.append(option['length'])
                created_info.append(option['data'])
        elif info['code'] == chr(0x02):

            link_ok = False
            for option in info['options']:
                if option['type'] == chr(0x03):
                    check_ip = option['data'].encode('hex')
                    check_ip = zip(check_ip[::2], check_ip[1::2])
                    check_ip = map(lambda c: str(int(''.join(c), 16)), check_ip)
                    check_ip = '.'.join(check_ip)

                    if check_ip == self._OPTIONS['local_ip']:
                        link_ok = True
                        break

            if link_ok is True and self._STATUS is None:
                #self._STATUS = 'ESTABLISHED'
                #self._PPP._DEBUG = False

                print '%s IP address %s' % ('local'.ljust(6), self._OPTIONS['local_ip'])
                print '%s IP address %s' % ('remote'.ljust(6), self._OPTIONS['remote_ip'])

            return -3

        created_info = ''.join(created_info)

        return created_info

    def run(self, init=False):

        try:
            if init is True:
                outputInfo = self.getConfigRequest()
            else:
                parsedInfo = self.parseInfo(self.inputInfo.pop(0))

                if self._PPP._DEBUG is True:
                    self.printDebug('rcvd', parsedInfo)
                outputInfo = self.createInfo(parsedInfo)

            if self._PPP._DEBUG is True and outputInfo != -3:
                parsed_info = self.parseInfo(outputInfo[2:])
                self.printDebug('sent', parsed_info)

            self.outputInfo.append(outputInfo)
        except Exception as e:
            #print str(e)
            self.outputInfo.append(-3)
