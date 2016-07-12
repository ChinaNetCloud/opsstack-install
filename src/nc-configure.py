#!/usr/bin/python

from lib import system
from lib.utils import argparse
from lib.utils import args


# TODO: Check if system has already been configured before, yes - verify to reconfigure
# TODO: Find a unique identifier for the server (MAC? IP? Keys? All of the above?)
# TODO: Instead of failing on finding Zabbix installed, verify if it is installed by us, if not exit, else reconfigure


def main():
    system.load().before_configure()
    system.load().configure()
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CNC configuration tool')
    parser.add_argument('-d', '--dry-run', action='store_true', dest='DRY_RUN')
    args.set_args(parser.parse_args())
    main()
else:
    print("Should be executed as main script!")
    exit(1)
