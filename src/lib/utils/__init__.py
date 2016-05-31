import socket
import subprocess
import sys

from lib import facts

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


def execute(cmd):
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = child.communicate()
    rc = child.returncode
    return rc, stdout, stderr


def is_app_installed(app_name):
    result = True
    if facts.collect_facts().os_name in ['centos', 'redhat']:
        # 1. get list of all packages installed
        rc, stdout, stderr = execute("rpm -qa | grep " + app_name)
        if stdout == "" and stderr == "" and rc == 1:
            # app_name is not installed as rpm package
            result = False
    return result


def is_proc_running(proc_name):
    result = True
    if facts.collect_facts().os_name in ['centos', 'redhat']:
        rc, stdout, stderr = execute("ps faux | grep -v grep | grep " + proc_name)
        if stdout == "" and stderr == "" and rc == 1:
            # proc_name not found
            result = False
    return result


def is_port_free(port_number):
    result = True
    if facts.collect_facts().os_name in ['centos', 'redhat']:
        try:
            sock = socket.socket(socket.SO_REUSEPORT, socket.SO_REUSEADDR)
            sock.bind(('', port_number))
            sock.listen(5)
            sock.close()
        except:
            result = False
    return result


if __name__ == '__main__':
    exit(1)
