import subprocess
import sys
import gettext
import getpass
import hashlib
import socket
import uuid
import os
import fcntl
import struct
import psutil
import args as arguments

from lib import log

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[1;34m'
NOCOLOR = '\033[0m'

OUT_MESSAGE = None

bin_path = sys.path[0]

PLAYS_PATH = os.path.abspath(os.path.dirname(__file__) + "/../../ansible/plays/")


def language_translation(msg):
    try:
        t = gettext.translation('translations', bin_path + '/locale', fallback=True)
        _ = t.ugettext
        message = _(msg)
    except UnicodeDecodeError:
        message = msg
    return message


def out_progress_wait(message):
    global OUT_MESSAGE
    message = language_translation(message)
    OUT_MESSAGE = message
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
    message = "\n".join(["  => " + s for s in message.split("\n")])
    sys.stdout.write(message + '\n')
    sys.stdout.flush()


def err(message):
    message = language_translation(message)
    sys.stderr.write('  ' + RED + '!! ' + message + NOCOLOR + '\n')
    sys.stderr.flush()


def execute(cmd):
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=PLAYS_PATH)
    output, stderr = child.communicate()
    rc = child.returncode
    return rc, output, stderr


def executable(cmd):
    result = False
    child = subprocess.Popen('command -V ' + cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=PLAYS_PATH)
    rc = child.wait()
    if rc == 0:
        result = True
    return result


def prompt(prompt_string):
    prompt_string = language_translation(prompt_string)
    prompt_string = "\n".join(["  => " + s for s in prompt_string.split("\n")])
    sys.stdout.write(prompt_string + ': ')
    result = raw_input("")
    return result


def prompt_pass(pass_string):
    pass_string = language_translation(pass_string)
    pass_string = "\n".join(["  => " + s for s in pass_string.split("\n")])
    result = getpass.getpass(pass_string + ': ')
    return result


def print_str(s, *args):
    result = s
    s = language_translation(s)
    try:
        result = (s % args)
    except TypeError:
        pass
    return result


def confirm(prompt_string, *args):
    # If assume-yes is on, don't prompt, return True
    if arguments.get_args().assume_yes is True:
        return True
    prompt_string = language_translation(prompt_string)
    while True:
        result = prompt(prompt_string + " [Y/n]")
        if result in ["", "y", "Y", "Yes", "YES"]:
            return True
        elif result in ["n", "N", "No", "NO"]:
            return False
        else:
            print ""
            continue


def batch_install_tag():
    # If batch_install is on, batch-install, return True
    if arguments.get_args().batch_install is True:
        return True
    else:
        return False


def ansible_play(name, extra_vars=None):
    plays_folder = PLAYS_PATH + "/"
    if extra_vars is None:
        playbook_cmd = "ansible-playbook " + plays_folder + name + ".playbook.yml"
    else:
        playbook_cmd = "ansible-playbook " + plays_folder + name + ".playbook.yml" + " --extra-vars \'" + extra_vars + "\'"
    rc, stdout, stderr = execute(playbook_cmd)
    if rc != 0:
        log.get_logger().log("Running playbook %s failed. Please see output below" % name)
        log.get_logger().log(playbook_cmd)
        log.get_logger().log(stdout)
        log.get_logger().log(stderr)
    return rc, stdout, stderr


def lock_file_exists(name):
    result = False
    lock_folder = os.path.abspath(os.path.dirname(__file__) + "/../../") + "/ansible/locks/"
    if os.path.isfile(lock_folder + name + ".lock"):
        result = True
    return result


def lock_file_create(name):
    lock_folder = os.path.abspath(os.path.dirname(__file__) + "/../../") + "/ansible/locks/"
    if not os.path.isfile(lock_folder + name + ".lock"):
        open(lock_folder + name + ".lock", "w").close()
        os.chmod(lock_folder + name + ".lock", 000)


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


def get_machine_id():
    result = ""
    # Get ssh_host_key md5
    key_md5 = ""
    key_path = "/etc/ssh/ssh_host_key"
    if os.path.isfile(key_path):
        with open(key_path, "rb") as f:
            c = f.read()
            key_md5 = hashlib.md5(c).hexdigest()
    # Get OpsStack visible IP address
    ip_address = ""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("opsstack.chinanetcloud.com", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except socket.error:
        # FIXME: Couldn't connect to OpsStack. Need better handling?
        pass
    # Get UUID which is actuall MAC of first HW interface
    mac = str(uuid.getnode())
    # Glue them altogether and get final ID
    result = hashlib.md5(key_md5 + ip_address + mac).hexdigest()
    return result


def verify_root_permissions():
    if not os.geteuid() == 0:
        return False
    else:
        return True


def get_iface_list():
    #return os.listdir("/sys/class/net/")
    return psutil.net_if_addrs().keys()


def iface_get_info(ifname):
    iface_info = {
        'ipv4': '',
        'ipv6': '',
        'mac': '',
        'type': 'physical'
    }
    try:
        if_info = psutil.net_if_addrs()[ifname]
        for info in if_info:
            # If family is 2, then it's the ipv4 address.
            # There might be more one ipv4 address in one interface,
            # we will only get the first one as the others might be virtual ip, see example below:
            '''[snic(family=2, address='43.254.52.101', netmask='255.255.255.224', broadcast='43.254.52.127', ptp=None),
                snic(family=2, address='43.254.52.99', netmask='255.255.255.255', broadcast='43.254.52.99', ptp=None),
                snic(family=10, address='fe80::f21f:afff:fede:e7bc%em1', netmask='ffff:ffff:ffff:ffff::', broadcast=None, ptp=None),
                snic(family=17, address='f0:1f:af:de:e7:bc', netmask=None, broadcast='ff:ff:ff:ff:ff:ff', ptp=None)]'''
            if info.family == 2 and iface_info['ipv4'] == '':
                iface_info['ipv4'] = info.address
            # if family is 10, then it's the ipv6 address
            elif info.family == 10:
                iface_info['ipv6'] = info.address.split('%')[0]
            # if family is 17, then it's the mac address
            elif info.family == 17:
                iface_info['mac'] = info.address
    except KeyError as e:
        log.get_logger().log("Failed to get ip address info for interface %s. Please see output below" % ifname)
        log.get_logger().log(e)
    return iface_info


def iface_get_mac_address(ifname):
    result = ""
    if os.path.isfile("/sys/class/net/" + ifname + "/address"):
        with open("/sys/class/net/" + ifname + "/address") as f:
            result = f.read().strip()
    return result


def iface_get_ip4_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


def iface_get_ip6_address(ifname):
    # FIXME: Detect real IPv6 address
    return ""


def iface_get_type(ifname):
    # FIXME: Detect real type
    return "physical"


if __name__ == '__main__':
    exit(1)
