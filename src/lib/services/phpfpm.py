import abstract
import os

from lib import utils

class Phpfpm(abstract.Abstract):
    def __init__(self):
        abstract.Abstract.__init__(self)

    @staticmethod
    def getname():
        return 'php-fpm'

    @staticmethod
    def discover(system):
        result = False
        if system.os == 'linux':
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
        if not result:
            utils.out(utils.print_str("NOT_DETECT_CONF_PATH", Phpfpm.getname()))
            utils.out("please configure manually refer to our docs: www.chinanetcloud.com/phpfpm-monitoring\n")
            return
        if utils.confirm(utils.print_str("RESTART_SERVICE", Phpfpm.getname())):
            phpfpm_restart = "true"
        utils.out_progress_wait(utils.print_str("CONFIGURE_MONITOR", Phpfpm.getname()))
        rc, out, err = utils.ansible_play("phpfpm_monitoring", "phpfpm_restart=%s" % (phpfpm_restart))
        if rc == 0:
            utils.out_progress_done()
        else:
            utils.out_progress_fail()
            utils.err(utils.print_str("FAILED_CONFIGURE_MONITOR", Phpfpm.getname()))
            exit(1)

