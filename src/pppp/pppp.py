import os
import sys
import socket

import termios
import fcntl

BAUDRATE = termios.B38400
SERIALDEVICE = '/dev/ttyS0'

BUFF_SIZE = 255

# Open serial device
try:
    fd = os.open(SERIALDEVICE, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
except:
    print 'ERROR : No such device %s' % SERIALDEVICE
    sys.exit(-1)

# Initialize attributes
tio = [0] * 7
tio[6] = [0] * 32

tio[0] = termios.IGNPAR | termios.ICRNL # c_iflag
tio[2] = BAUDRATE | termios.CRTSCTS | termios.CS8 | termios.CLOCAL | termios.CREAD # c_cflag

termios.tcflush(fd, termios.TCIFLUSH)
termios.tcsetattr(fd, termios.TCSANOW, tio)

while(1):
    # implement PPP state machine in here!!!!

    res = os.read(fd, BUFF_SIZE)

    # Needs frame module to frame packets
    # blah blah

    snd = os.write(fd, res)

os.close(fd)
