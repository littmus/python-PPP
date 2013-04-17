import os
import sys
import socket

import termios
import fcntl

BAUDRATE = 38400
SERIALDEVICE = '/dev/ttyS0'

fd = os.open(SERIALDEVICE, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
if fd < 0:
	print "error"
