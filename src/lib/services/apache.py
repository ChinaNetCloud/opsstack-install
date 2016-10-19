import abstract
import os
import re

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
        if system.os == 'linux':
            if system.is_proc_running("httpd") or system.is_app_installed("httpd"):
                result = True
        return result

    @staticmethod
    def getconf(system):
        result = False
        httpd_conf = None
        httpd_dir = None
        rc, out, err = utils.execute("httpd -V")
        if rc == 0 and out != "":
            for line in out.split('\n'):
                if re.search(r'(HTTPD_ROOT=\".*\")', line):
                    conf_dir = re.search(r'(HTTPD_ROOT=\".*\")', line).group(1).split("=")[1].strip('\"\'')
                elif re.search(r'(SERVER_CONFIG_FILE=\".*\")', line):
                    conf_file = re.search(r'(SERVER_CONFIG_FILE=\".*\")', line).group(1).split("=")[1].strip('\"\'')
            if conf_dir != "" and conf_file != "":
                httpd_conf = os.path.join(conf_dir, conf_file)
                httpd_dir = os.path.split(os.path.dirname(httpd_conf))[0]
                if os.path.exists(httpd_conf):
                    result = True
        return result, httpd_conf, httpd_dir

    @staticmethod
    def configure(system):
        httpd_restart = "false"
        httpd_start = "false"
        result, httpd_conf, httpd_dir = Apache.getconf(system)
        if not result:
            utils.out(utils.print_str("NOT_DETECT_CONF_PATH", Apache.getname()))
            utils.out("please configure manually refer to our docs: www.chinanetcloud.com/nginx-monitoring\n")
            return
        if system.is_proc_running("httpd"):
            if utils.confirm(utils.print_str("RESTART_SERVICE", Apache.getname())):
                httpd_restart = "true"
            else:
                utils.out_progress_info(utils.print_str("RESTART_SERVICE_LATER", Apache.getname()))
        else:
            if utils.confirm(utils.print_str("START_SERVICE", Apache.getname())):
                httpd_start = "true"
            else:
                utils.out_progress_info(utils.print_str("START_SERVICE_LATER", Apache.getname()))
        utils.out_progress_wait(utils.print_str("CONFIGURE_MONITOR", Apache.getname()))
        rc, out, err = utils.ansible_play("apache_monitoring", "httpd_dir=%s httpd_conf=%s httpd_restart=%s httpd_start=%s" % (httpd_dir, httpd_conf, httpd_restart, httpd_start))
        if rc == 0:
            utils.out_progress_done()
        else:
            utils.out_progress_fail()
            utils.err(utils.print_str("FAILED_CONFIGURE_MONITOR", Apache.getname()))
            exit(1)
