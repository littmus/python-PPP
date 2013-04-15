import os
import sys
import socket

import termios
import fcntl

BAUDRATE = 38400
SERIALDEVICE = '/dev/ttyS0'

