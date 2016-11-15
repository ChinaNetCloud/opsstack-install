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
            if system.is_proc_running("java.*Xms.*Xmx"):
                result = True
        return result

    @staticmethod
    def configure(system):
        cmd_bin = "ps -e -o command | grep -v 'grep' | grep 'java.*Xms.*Xmx' | awk '{ print $1 }' | head -n1"
        jrc, jout, jerr = utils.execute(cmd_bin)
        if jrc == 0 and jout != "":
            java_bin = jout.strip()
        else:
            java_bin = utils.prompt(utils.print_str("SERVICE_BIN_PATH", Java.getname()))
        utils.out_progress_wait(utils.print_str("CONFIGURE_JAVA_MONITOR"))
        cmd_jmxports = "ps -e -o command | grep %s | grep 'jmxremote.port' | grep -v grep | " \
              "awk -F'jmxremote.port=' '{ print $2 }' | awk '{ print $1 }'" % Java.getname()
        jmxrc, jmxout, jmxerr = utils.execute(cmd_jmxports)
        if jmxrc != 0 or jmxout == "":
            utils.out_progress_fail()
            utils.out(utils.print_str("JMX_PORT_NOT_OPEN"))
            utils.out(utils.print_str("CONFIGURE_JAVA_MANUALLY"))
            exit(1)
        else:
            for port in jmxout.strip().split('\n'):
                cmd_jmxcheck = "%s -jar /home/zabbix/bin/cmdline-jmxclient-0.10.3.jar " \
                          "zabbix_check:zabbix_check 127.0.0.1:%s" % (java_bin, port)
                rc, out, err = utils.execute(cmd_jmxcheck)
                if rc != 0:
                    utils.out_progress_fail()
                    utils.out(utils.print_str("ZABBIX_NO_ACCESS", port))
                    utils.out(utils.print_str("CONFIGURE_JAVA_MANUALLY"))
            utils.out_progress_done()

