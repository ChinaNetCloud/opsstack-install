import abstract

from lib import utils


class Java(abstract.Abstract):
    def __init__(self):
        abstract.Abstract.__init__(self)

    @staticmethod
    def getname():
        return 'java'

    @staticmethod
    def discover(system):
        result = False
        if system.os == 'linux':
            if system.is_proc_running("java") and Java.get_binary() is not None:
                result = True
        return result

    @staticmethod
    def get_binary():
        java_bin = None
        java_bin_cmd = "ps -e -o command | grep -v 'grep' | awk '{ print $1 }' | grep 'java'"
        rc, out, err = utils.execute(java_bin_cmd)
        if rc == 0 and out != '':
            binarys = out.strip().splitlines()
            for binary in binarys:
                if utils.executable(binary):
                    java_bin = binary
                    break
        return java_bin

    @staticmethod
    def configure(system):
        java_bin = Java.get_binary()
        utils.out_progress_wait(utils.print_str("CONFIGURE_JAVA_MONITOR"))
        cmd_jmxports = "ps -e -o command | grep %s | grep 'jmxremote.port' | grep -v grep | " \
              "awk -F'jmxremote.port=' '{ print $2 }' | awk '{ print $1 }'" % Java.getname()
        jmxrc, jmxout, jmxerr = utils.execute(cmd_jmxports)
        if jmxrc != 0 or jmxout == "":
            utils.out_progress_fail()
            utils.out(utils.print_str("JMX_PORT_NOT_OPEN"))
            utils.out(utils.print_str("CONFIGURE_JAVA_MANUALLY"))
        else:
            for port in jmxout.strip().split('\n'):
                cmd_jmxcheck = "%s -jar /var/lib/nc_zabbix/bin/cmdline-jmxclient-0.10.3.jar " \
                          "zabbix_check:zabbix_check 127.0.0.1:%s" % (java_bin, port)
                rc, out, err = utils.execute(cmd_jmxcheck)
                if rc != 0:
                    utils.out_progress_fail()
                    utils.out(utils.print_str("ZABBIX_NO_ACCESS", port))
                    utils.out(utils.print_str("CONFIGURE_JAVA_MANUALLY"))
            utils.out_progress_done()

