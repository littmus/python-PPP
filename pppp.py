import os
import sys
import termios
import re
import time

from pppp import PPP
from pppp.hdlc import HDLC

BAUDRATE = None
SERIALDEVICE = None

LOCAL_IP = None
REMOTE_IP = None

BUFF_SIZE = 1500

ERROR_NO_ARGUMENTS = -1
ERROR_NO_DEVICES = -2

IP_PRINT_FORMAT = '%s IP address %s'  # (local , remote), ip
IP_REGEX = r'^(25[0-5]|(2[0-4]|1\d|\d)?\d.){3}(25[0-5]|(2[0-4]|1\d|\d)?\d):(25[0-5]|(2[0-4]|1\d|\d)?\d.){3}(25[0-5]|(2[0-4]|1\d|\d)?\d)$'


def main(argv):

    if len(argv) == 0:
        return ERROR_NO_ARGUMENTS

    # Processing arguments
    # Need to change by using argparser
    # import argparser
    options = {
        'debug': False,
        'noaccomp': False,
        'nopcomp': False,
        'local_ip': '',
        'remote_ip': '',
        'device': '',
        'speed': '',
    }

    for arg in argv:

        # Get ttyname
        if re.match(r'^/dev/tty\w+$', arg):
            SERIALDEVICE = arg
            options['device'] = arg
        elif re.match(r'^tty\w+$', arg):
            SERIALDEVICE = '/dev/' + arg
            options['device'] = arg
        # Get debug option
        elif re.match(r'^debug$', arg):
            options['debug'] = True
        # Get spped
        elif re.match(r'^\d+$', arg):
            options['speed'] = arg
            try:
                BAUDRATE = getattr(termios, 'B' + arg)
            except:
                BAUDRATE = termios.B0
        # Get Local/Remote IP address
        elif re.match(IP_REGEX, arg):
            options['local_ip'], options['remote_ip'] = arg.split(':')
        # Get accomp option
        elif re.match(r'^noaccomp$', arg):
            options['noaccomp'] = True
        # Get pcomp option
        elif re.match(r'^nopcomp$', arg):
            options['nopcomp'] = True

    # Open serial device
    try:
        fd = os.open(SERIALDEVICE, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except:
        print 'ERROR : No such device : %s' % SERIALDEVICE
        return ERROR_NO_DEVICES

    # Initialize attributes
    tio = [0] * 7
    tio[6] = [0] * 32

    # c_iflag
    tio[0] = termios.IGNPAR | termios.ICRNL
    # c_cflag
    tio[2] = BAUDRATE | termios.CRTSCTS
    tio[2] = tio[2] | termios.CS8 | termios.CLOCAL | termios.CREAD

    termios.tcflush(fd, termios.TCIFLUSH)
    termios.tcsetattr(fd, termios.TCSANOW, tio)

    pppp = PPP(framer=HDLC(), options=options)
    STOP = False
    TIMEOUT_COUNT = 10
    COUNT = 0
    while not STOP:
        try:
            recv_packet = os.read(fd, BUFF_SIZE)

            if pppp._STATE == 0:
                pppp.run(income=False)

            if recv_packet:
                pppp._STATE = 1
                pppp.putPacket(recv_packet)

                pppp.run()

                send_packet = pppp.getPacket()

                if send_packet not in [-1, -2, -3]:
                    os.write(fd, send_packet)
                else:
                    pass
            else:
                if pppp._STATE == 0:
                    time.sleep(3)
                    COUNT += 1
                    if COUNT >= TIMEOUT_COUNT:
                        print 'LCP: timeout sending Config-Requests'
                        break
        except:
            pass

    os.close(fd)
    print 'Modem hangup'

    return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
