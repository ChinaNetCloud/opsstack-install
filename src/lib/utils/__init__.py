import subprocess
import sys
import os
import socket

import gettext

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[1;34m'
NOCOLOR = '\033[0m'

OUT_MESSAGE = None


def language_translation(msg):
    t = gettext.translation('nc-configure', 'locale', fallback=True)
    _ = t.ugettext
    message = _(msg)
    return message

def out_progress_wait(message):
    global OUT_MESSAGE
    OUT_MESSAGE = language_translation(message)
    sys.stdout.write('  => [ .... ] ' + OUT_MESSAGE)
    sys.stdout.flush()


def out_progress_skip():
    global OUT_MESSAGE
    sys.stdout.write('\r')
    msg = language_translation('SKIP')
    sys.stdout.write('  => [ ' + YELLOW + msg + NOCOLOR + ' ] ' + OUT_MESSAGE + "\n")
    sys.stdout.flush()


def out_progress_done():
    global OUT_MESSAGE
    sys.stdout.write('\r')
    msg = language_translation('DONE')
    sys.stdout.write('  => [ ' + GREEN + msg + NOCOLOR + ' ] ' + OUT_MESSAGE + "\n")
    sys.stdout.flush()


def out_progress_fail():
    global OUT_MESSAGE
    sys.stdout.write('\r')
    msg = language_translation('FAIL')
    sys.stdout.write('  => [ ' + RED + msg + NOCOLOR + ' ] ' + OUT_MESSAGE + "\n")
    sys.stdout.flush()


def out_progress_info(message):
    msg = language_translation('INFO')
    sys.stdout.write('  => [ ' + BLUE + msg + NOCOLOR + ' ] ' + message + "\n")
    sys.stdout.flush()


def out(message):
    message = language_translation(message)
    sys.stderr.write(message)
    sys.stderr.flush()


def err(message):
    message = language_translation(message)
    sys.stderr.write('\n  ' + RED + '!! ' + message + NOCOLOR + '\n\n')
    sys.stderr.flush()


def execute(cmd):
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = child.communicate()
    rc = child.returncode
    return rc, stdout, stderr


def prompt(prompt_string):
    print("")
    prompt_string = language_translation(prompt_string)
    result = input(prompt_string)
    print("")
    return result


def confirm(prompt_string):
    prompt_string = language_translation(prompt_string)
    while True:
        print("")
        result = prompt(prompt_string + " [Y/n]:")
        if result in ["", "y", "Y", "Yes", "YES"]:
            return True
        elif result in ["n", "N", "No", "NO"]:
            return False
        else:
            continue


def ansible_play(name):
    return execute("ansible-playbook " + os.path.abspath(os.path.dirname(__file__) + "/../../") + "/ansible/plays/" + name + ".playbook.yml")


def test_connection(host, port):
    result = False
    sock = socket.socket()
    try:
        sock.connect((host, port))
        sock.close()
        result = True
    except socket.error:
        result = False
    return result


# Define input for 2.x
try:
    input = raw_input
except NameError:
    pass

if __name__ == '__main__':
    exit(1)
