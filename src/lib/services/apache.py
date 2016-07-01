import abstract
import os

from lib import utils

class Apache(abstract.Abstract):
    def __init__(self):
        abstract.Abstract.__init__(self)

    @staticmethod
    def getname():
        return 'apache'

    @staticmethod
    def discover(system):
        result = False
        if system.OS == 'linux':
            if system.is_proc_running("httpd") or system.is_app_installed("httpd"):
                result = True
        return result

    @staticmethod
    def configure(system):
        utils.out_progress_wait("Configuring apache monitoring...")
        if not system.config.get("apache_monitoring_configured") == "yes" and not os.path.isfile('/etc/httpd/conf.d/zabbix.conf'):
            rc, out, err = utils.ansible_play("rhel_apache_monitoring")
            if rc == 0:
                system.config.set("apache_monitoring_configured", "yes")
                utils.out_progress_done()
            else:
                utils.out_progress_fail()
                utils.err("Failed to install apache monitoring")
                exit(1)
        else:
            utils.out_progress_skip()
