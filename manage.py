#!/usr/bin/env python

# -*- coding: utf-8 -*-
import argparse
from apps.core.manager import managers
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Tornado web shell')
    subparsers = parser.add_subparsers()
    for manage in managers:
        manage(subparsers)
    args = parser.parse_args()
    args.func(args)
