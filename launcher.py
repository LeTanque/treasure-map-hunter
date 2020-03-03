#!/usr/bin/env python3
import sys
from follow_path import Follow


if len(sys.argv) <= 3:
    print("\nError: Please include map, start, and end\n")
    print("python3 launcher.py {map_name} {start} {end} {verbosity}")
    print(" > map_name = JSON file\n")
    print(" > start = integer\n")
    print(" > end = integer\n")
    print(" > verbosity = integer\n")
elif len(sys.argv) == 4:
    follow = Follow(sys.argv[1], sys.argv[2], sys.argv[3])
elif len(sys.argv) == 5:
    follow = Follow(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
