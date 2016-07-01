import abstract
import os

from lib import utils

class Nginx(abstract.Abstract):
    def __init__(self):
        abstract.Abstract.__init__(self)

    @staticmethod
    def getname():
        return 'nginx'

    @staticmethod
    def discover(system):
        result = False
        if system.OS == 'linux':
            if system.is_proc_running("nginx") or system.is_app_installed("nginx"):
                result = True
        return result

    @staticmethod
    def configure(system):
        utils.out_progress_wait("Configuring nginx monitoring...")
        #TODO ask customer to input nginx configuretaion folder if not in default folder /etc/nginx/conf.d ?
        if not system.config.get("nginx_monitoring_configured") == "yes" and not os.path.exists('/etc/nginx/conf.d/zabbix.conf'):
            rc, out, err = utils.ansible_play("rhel_nginx_monitoring")
            if rc == 0:
                system.config.set("nginx_monitoring_configured", "yes")
                utils.out_progress_done()
            else:
                utils.out_progress_fail()
                utils.err("Failed to install nginx monitoring")
                exit(1)
        else:
            utils.out_progress_skip()
