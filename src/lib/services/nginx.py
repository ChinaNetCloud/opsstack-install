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
	result = True
	if not system.config.get("nginx_vars") == "yes":
            rc, out, err = utils.execute("nginx -V")
            # The nginx configure parameters will be wrote to stderr
            if rc == 0 and err != "":
                if re.match(r".*(\-\-conf\-path\=.*nginx\.conf).*", err.split('\n')[-2]):
                    info = re.match(r".*(\-\-conf\-path\=.*nginx\.conf).*", err.split('\n')[-2]).group(1)
                    conf_file = info.split('=')[1]
                    conf_dir = os.path.dirname(conf_file)
            else:
                result = False
            plays_vars = os.path.abspath(os.path.dirname(__file__) + "/../../") + "/ansible/plays/variables.yml"
            with open(plays_vars, 'a') as f:
                f.write("nginx_conf_file: %s\n" % conf_file)
                f.write("nginx_conf_dir: %s\n" % conf_dir)
            if utils.confirm("Do you want to restart '%s' after configure monitoring?" % Nginx.getname()):
                with open(plays_vars, 'a') as f:
                    f.write("nginx_restart: yes")
            else:
                utils.out("Please restart nginx manually later so that it can be monitored")
                with open(plays_vars, 'a') as f:
                    f.write("nginx_restart: no")
            system.config.set("nginx_vars", "yes")
	return result

    @staticmethod
    def configure(system):
        utils.out_progress_wait("Configuring '%s' monitoring..." % Nginx.getname())
	if not Nginx.getconf(system):
	    utils.out("Could not detect '%s' configuration path,\n" % Nginx.getname())
            utils.out("please configure manually refer to our docs: www.chinanetcloud.com/nginx-monitoring\n")
            system.config.set("nginx_monitoring_configured", "yes")
	    return
        if not system.config.get("nginx_monitoring_configured") == "yes":
            rc, out, err = utils.ansible_play("rhel_nginx_monitoring")
            if rc == 0:
                system.config.set("nginx_monitoring_configured", "yes")
                utils.out_progress_done()
            else:
                utils.out_progress_fail()
                utils.err("Failed to install '%s' monitoring" % Nginx.getname())
                exit(1)
        else:
            utils.out_progress_skip()
