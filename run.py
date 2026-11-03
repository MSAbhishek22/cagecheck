#!/usr/bin/env python3
"""CageCheck entry point — fresh build, Vultr Agent Rush, Challenge 1."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.server import main

if __name__ == "__main__":
    main()
