#!/usr/bin/env python3
import sys
from cpu2 import *


if len(sys.argv) == 1:
    print("\nError: Please include program!\n")
    print(" ./ls8.py {filename} {verbosity}")
    print(" > verbosity = integer\n")
elif len(sys.argv) == 2:
    print('len(sys.argv):>= 2 ', len(sys.argv), sys.argv)
    cpu = CPU(sys.argv[1])
elif len(sys.argv) >= 3:
    print('len(sys.argv):>= 3 ', len(sys.argv))
    cpu = CPU(sys.argv[1], sys.argv[2])

