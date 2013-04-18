import os
import sys
import socket

import termios
import fcntl

BAUDRATE = termios.B38400
SERIALDEVICE = '/dev/ttyS0'

BUFF = ''
BUFF_SIZE = 255

try:
    fd = os.open(SERIALDEVICE, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
except:
    print 'ERROR : No such device %s' % SERIALDEVICE
    sys.exit(-1)

c_cflag = BAUDRATE | termios.CRTSCTS | termios.CS8 | termios.CLOCAL | termios.CREAD
c_iflag = termios.IGNPAR | termios.ICRNL

fd_attrs = termios.tcgetattr(fd)

for i in range(0, len(fd_attrs) - 1):
    fd_attrs[i] = 0

for i in range(0, len(fd_attrs[len(fd_attrs) - 1])):
    fd_attrs[len(fd_attrs) - 1][i] = 0

fd_attrs[0] = c_iflag
fd_attrs[2] = c_cflag

termios.tcflush(fd, termios.TCIFLUSH)
termios.tcsetattr(fd, termios.TCSANOW, fd_attrs)

print termios.tcgetattr(fd)

while(1):
    res = os.read(fd, BUFF_SIZE)
    snd = os.write(fd, res)

    # implement PPP state machine in here!!!!

os.close(fd)
