#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Vasplib development team (Zhuang's Lab at ASU).

import sys
import argparse
from vasplib import info
from vasplib.analysis.electronic import get_electronic_property

"""
A master script with many tools for driving vasplib.
"""

def main():
    info()
    print("Description\n------------")
    parser = argparse.ArgumentParser(description="""
    vasplib is a convenient script that interacts with vasp and dft 
    calculations This script works based on several sub-commands with 
    their own options. To see the options for the sub-commands, type 
    "vasplib sub-command -h".""")

    subparsers = parser.add_subparsers()

    # electronic properties
    parser_electronic = subparsers.add_parser(
        "electronic", help="Analyzing the electronic dos and band structure from 'vasprun.xml' files.")
    parser_electronic.add_argument('PARAM', type=str, 
                             help="parameter file, json format")
    parser_electronic.add_argument('FILE', type=str,
                             help="path to vasprun.xml file")
    parser_electronic.set_defaults(func=get_electronic_property)

    args = parser.parse_args()

    try:
        getattr(args, "func")
    except AttributeError:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()