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
		nginx_restart = "no"
        utils.out_progress_wait("Configuring '%s' monitoring..." % Nginx.getname())
        result, nginx_file, nginx_dir = Nginx.getconf(system)
		if result == False:
	    	utils.out("Could not detect '%s' configuration path,\n" % Nginx.getname())
            utils.out("please configure manually refer to our docs: www.chinanetcloud.com/nginx-monitoring\n")
	    	return
		if utils.confirm("Do you want to restart '%s' after configure monitoring?" % Nginx.getname()):
			nginx_restart = "yes"
        if not system.config.get("nginx_monitoring_configured") == "yes":
            rc, out, err = utils.ansible_play("rhel_nginx_monitoring", "nginx_conf_dir=%s nginx_conf_file=%s nginx_restart =%s" % (nginx_file, nginx_dir, nginx_restart))
            if rc == 0:
                system.config.set("nginx_monitoring_configured", "yes")
                utils.out_progress_done()
            else:
                utils.out_progress_fail()
                utils.err("Failed to install '%s' monitoring" % Nginx.getname())
                exit(1)
        else:
            utils.out_progress_skip()
