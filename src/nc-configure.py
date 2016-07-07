#!/usr/bin/python

from lib import system


# TODO: Check if system has already been configured before, yes - verify to reconfigure
# TODO: Find a unique identifier for the server (MAC? IP? Keys? All of the above?)
# TODO: Instead of failing on finding Zabbix installed, verify if it is installed by us, if not exit, else reconfigure


def main():
    system.load().before_configure()
    system.load().configure()
    pass

if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    main()
else:
    print("Should be executed as main script!")
    exit(1)
