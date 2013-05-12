import os
import sys
import termios
import re

from ppp import PPP
from hdlc import HDLC


DEBUG = False

BAUDRATE = None
SERIALDEVICE = None

LOCAL_IP = None
REMOTE_IP = None

BUFF_SIZE = 1502

ERROR_NO_ARGUMENTS = -1
ERROR_NO_DEVICES = -2

DEBIG_PRINT_FORMAT = '%s [%s %s id=%x %s]'  # (rcvd, sent) , (protocol), (state), (id), (option)
IP_PRINT_FORMAT = '%s IP address %s'  # (local , remote), ip
IP_REGEX = r'^(25[0-5]|(2[0-4]|1\d|\d)?\d.){3}(25[0-5]|(2[0-4]|1\d|\d)?\d)$'


def main(argv):

    if len(argv) == 0:
        return ERROR_NO_ARGUMENTS

    # Processing arguments
    # Need to change by using argparser
    # import argparser
    for arg in argv:

        # Get ttyname
        if re.match(r'^/dev/tty\w+$', arg):
            SERIALDEVICE = arg
        elif re.match(r'^tty\w+$', arg):
            SERIALDEVICE = '/dev/' + arg
        elif re.match(r'^debug$', arg):
            DEBUG = True
        # Get spped
        elif re.match(r'^\d+$', arg):
            try:
                BAUDRATE = getattr(termios, 'B' + arg)
            except:
                BAUDRATE = termios.B38400
        # Get Local/Remote IP address
        elif re.match(IP_REGEX + ':' + IP_REGEX, arg):
            LOCAL_IP, REMOTE_IP = arg.split(':')

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

    pppp = PPP(framer=HDLC())
    STOP = False

    while not STOP:
        # implement PPP state machine in here!!!!

        recv_packet = os.read(fd, BUFF_SIZE)

        if recv_packet:
            #print 'rcvd', recv_packet.encode('hex')
            pppp.putPacketToFramer(recv_packet)

            pppp.run()

            send_packet = pppp.getPacketFromFramer()
            if send_packet != -1:
                if os.write(fd, send_packet) > 0:
                    print 'sent', send_packet.encode('hex')

    os.close(fd)

    return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
