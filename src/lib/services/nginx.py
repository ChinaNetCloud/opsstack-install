import abstract
import os
import re

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
    def getconf(system):
        result = False
        conf_file = None 
        conf_dir = None 
        rc, out, err = utils.execute("nginx -V")
        # The nginx configure parameters will be wrote to stderr
        if rc == 0 and err != "":
            if re.match(r".*(\-\-conf\-path\=.*nginx\.conf).*", err.split('\n')[-2]):
                info = re.match(r".*(\-\-conf\-path\=.*nginx\.conf).*", err.split('\n')[-2]).group(1)
                conf_file = info.split('=')[1]
                conf_dir = os.path.dirname(conf_file)
                if os.path.exists(conf_file):
                    result = True
        return result, conf_file, conf_dir

    @staticmethod
    def configure(system):
        nginx_restart = "false"
        result, nginx_file, nginx_dir = Nginx.getconf(system)
        if not result:
            utils.out(utils.print_str("NOT_DETECT_CONF_PATH", Nginx.getname()))
            utils.out("please configure manually refer to our docs: www.chinanetcloud.com/nginx-monitoring\n")
            return
        if utils.confirm(utils.print_str("RESTART_SERVICE", Nginx.getname())):
            nginx_restart = "true"
        utils.out_progress_wait(utils.print_str("CONFIGURE_MONITOR", Nginx.getname()))
        if not system.config.get("nginx_monitoring_configured") == "yes":
            rc, out, err = utils.ansible_play("rhel_nginx_monitoring", "nginx_conf_dir=%s nginx_conf_file=%s nginx_restart=%s" % (nginx_dir, nginx_file, nginx_restart))
            if rc == 0:
                system.config.set("nginx_monitoring_configured", "yes")
                utils.out_progress_done()
            else:
                utils.out_progress_fail()
                utils.err(utils.print_str("FAILED_CONFIGURE_MONITOR", Nginx.getname()))
                exit(1)
        else:
            utils.out_progress_skip()
