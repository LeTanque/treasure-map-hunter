#!/usr/bin/env python3
import sys
from follow_path import Follow


if len(sys.argv) <= 2:
    print("\nError: Please include map, and end\n")
    print("python3 launcher.py {map_name} {end} {verbosity}")
    print(" > map_name = JSON file\n")
    print(" > start = integer\n")
    print(" > end = integer\n")
    print(" > verbosity = integer\n")
elif len(sys.argv) == 3:
    follow = Follow(sys.argv[1], sys.argv[2])
elif len(sys.argv) == 4:
    follow = Follow(sys.argv[1], sys.argv[2], sys.argv[3])
