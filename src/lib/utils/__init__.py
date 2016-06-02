import subprocess
import sys

RED = '\033[0;31m'
GREEN = '\033[0;32m'
NOCOLOR = '\033[0m'

OUT_MESSAGE = None


def out_progress_wait(message):
    global OUT_MESSAGE
    OUT_MESSAGE = message
    sys.stdout.write('  => [ .... ] ' + OUT_MESSAGE)
    sys.stdout.flush()


def out_progress_done():
    global OUT_MESSAGE
    sys.stdout.write('\r')
    sys.stdout.write('  => [ ' + GREEN + 'DONE' + NOCOLOR + ' ] ' + OUT_MESSAGE + "\n")
    sys.stdout.flush()


def out_progress_fail():
    global OUT_MESSAGE
    sys.stdout.write('\r')
    sys.stdout.write('  => [ ' + RED + 'FAIL' + NOCOLOR + ' ] ' + OUT_MESSAGE + "\n")
    sys.stdout.flush()


def out(message):
    sys.stderr.write('\n' + message + '\n\n')
    sys.stderr.flush()


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


def confirm(prompt_string):
    while True:
        print("")
        result = prompt(prompt_string + " [Y/n]:")
        if result in ["", "y", "Y", "Yes", "YES"]:
            return True
        elif result in ["n", "N", "No", "NO"]:
            return False
        else:
            continue


# Define input for 2.x
try:
    input = raw_input
except NameError:
    pass

if __name__ == '__main__':
    exit(1)
