import os
import sys

import termios
import fcntl

import re

from hdlc import HDLC


BAUDRATE = termios.B38400
BAUDRATE_NUM = None
SERIALDEVICE = None

LOCAL_IP = None
REMOTE_IP = None

BUFF_SIZE = 255

ERROR_NO_ARGUMENTS = -1
ERROR_NO_DEVICES = -2

DEBIG_PRINT_FORMAT = '%s [%s %s id=%x ]'
IP_REGEX = r'^(25[0-5]|(2[0-4]|1\d|\d)?\d.){3}(25[0-5]|(2[0-4]|1\d|\d)?\d)$'


def main(argv):

    if len(argv) == 0:
        return ERROR_NO_ARGUMENTS

    # Processing arguments
    for arg in argv:

        # Get ttyname
        if re.match(r'^/dev/\w+$', arg):
            SERIALDEVICE = arg
        # Get spped
        elif re.match(r'^\d+$', arg):
            BAUDRATE_NUM = int(arg)
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
    tio[2] = BAUDRATE | termios.CRTSCTS | termios.CS8 | termios.CLOCAL | termios.CREAD

    termios.tcflush(fd, termios.TCIFLUSH)
    termios.tcsetattr(fd, termios.TCSANOW, tio)

    while(1):
        # implement PPP state machine in here!!!!

        recv_frame = os.read(fd, BUFF_SIZE)

        if len(recv_frame) != 0:
            hdlc = HDLC(recv_frame.encode('hex'))

            print hdlc.parseFrame()

            #print 'rcvd ' + recv_frame.encode('hex')
        # Needs frame module to frame packets
        # blah blah

        send_frame = os.write(fd, recv_frame)

        if send_frame > 0:
            print 'sent ' + recv_frame.encode('hex')

        # send_frame = HDLC.
        # os.write(fd, send_frame)

    os.close(fd)

    return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
