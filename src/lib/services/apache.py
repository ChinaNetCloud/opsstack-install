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
        if system.OS == 'linux':
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
	result, httpd_conf, httpd_dir = Apache.getconf(system)
	if result == False:
            utils.out("Could not detect '%s' configuration path,\n" % Apache.getname())
            utils.out("please configure manually refer to our docs: www.chinanetcloud.com/nginx-monitoring\n")
            return
        if utils.confirm("RESTART_APACHE_SERVICE?"):
            httpd_restart = "true"
        utils.out_progress_wait("CONFIGURE_APACHE_MONITORING")
        if not system.config.get("apache_monitoring_configured") == "yes": 
            rc, out, err = utils.ansible_play("rhel_apache_monitoring", "httpd_dir=%s httpd_conf=%s httpd_restart=%s" % (httpd_dir, httpd_conf, httpd_restart))
            if rc == 0:
                system.config.set("apache_monitoring_configured", "yes")
                utils.out_progress_done()
            else:
                utils.out_progress_fail()
                utils.err("Failed to install apache monitoring")
                exit(1)
        else:
            utils.out_progress_skip()
