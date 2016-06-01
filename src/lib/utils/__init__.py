import subprocess
import sys

RED = '\033[0;31m'
GREEN = '\033[0;32m'
NOCOLOR = '\033[0m'


def out(message):
    sys.stdout.write('  => ' + message)
    sys.stdout.flush()


def out_ok():
    sys.stdout.write('\t\t\t[  ' + GREEN + 'OK' + NOCOLOR + '  ]\n')
    sys.stdout.flush()


def out_not_ok():
    sys.stdout.write('\t\t\t[  ' + RED + 'ERR' + NOCOLOR + '  ]\n')
    sys.stdout.flush()


def err(message):
    sys.stderr.write('\n  ' + RED + '!! ' + message + NOCOLOR + '\n\n')
    sys.stderr.flush()


def execute(cmd):
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = child.communicate()
    rc = child.returncode
    return rc, stdout, stderr


def prompt(prompt_string):
    print("")
    result = input(prompt_string)
    print("")
    return result


# Define input for 2.x
try:
    input = raw_input
except NameError:
    pass

if __name__ == '__main__':
    exit(1)
