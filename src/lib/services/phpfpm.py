import abstract
import os

from lib import utils

class Phpfpm(abstract.Abstract):
    def __init__(self):
        abstract.Abstract.__init__(self)

    @staticmethod
    def getname():
        return 'phpfpm'

    @staticmethod
    def discover(system):
        result = False
        if system.OS == 'linux':
            if system.is_proc_running("php-fpm") or system.is_app_installed("php-fpm"):
                result = True
        return result

    @staticmethod
    def getconf(system):
        result = False
        if os.path.exists("/etc/php-fpm.d/www.conf"):
            result = True
        return result

    @staticmethod
    def configure(system):
        phpfpm_restart = "false"
        result = Phpfpm.getconf(system)
        if result == False:
            utils.out("Could not detect '%s' configuration path,\n" % Phpfpm.getname())
            utils.out("please configure manually refer to our docs: www.chinanetcloud.com/phpfpm-monitoring\n")
            return
        if utils.confirm("RESTART_PHPFPM_SERVICE?"):
            phpfpm_restart = "true"
        utils.out_progress_wait("CONFIGURE_PHPFPM_MONITOR")
        if not system.config.get("phpfpm_monitoring_configured") == "yes":
            rc, out, err = utils.ansible_play("rhel_phpfpm_monitoring", "phpfpm_restart=%s" % (phpfpm_restart))
            if rc == 0:
                system.config.set("phpfpm_monitoring_configured", "yes")
                utils.out_progress_done()
            else:
                utils.out_progress_fail()
                utils.err("Failed to install '%s' monitoring" % Phpfpm.getname())
                exit(1)
        else:
            utils.out_progress_skip()
