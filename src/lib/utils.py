import sys

RED = '\033[0;31m'
GREEN = '\033[0;32m'
NOCOLOR = '\033[0m'


def out(message):
    sys.stdout.write('  => ' + message)


def out_ok():
    sys.stdout.write('\t\t\t[  ' + GREEN + 'OK' + NOCOLOR + '  ]\n')


def out_not_ok():
    sys.stdout.write('\t\t\t[  ' + RED + 'ERR' + NOCOLOR + '  ]\n')


def err(message):
    sys.stderr.write('\n  ' + RED + '!! ' + message + NOCOLOR + '\n\n')

if __name__ == '__main__':
    exit(1)
