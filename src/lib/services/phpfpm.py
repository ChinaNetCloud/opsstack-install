import abstract
import os
import psutil
import json
import re

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
            if system.is_proc_running("php5?\.?[3-6]?-fpm") or system.is_app_installed("php5?\.?[3-6]?-fpm"):
                result = True
        return result

    @staticmethod
    def getconf(system):
        pars = {}
        result = False
        phpfpm_bin = None
        phpfpm_config_path = None
        phpfpm_service_name = None
        phpfpm_conf_list = ['/etc/php-fpm.d/www.conf',
                            '/etc/php5/fpm/pool.d/www.conf',
                            '/etc/php/5.3/fpm/pool.d/www.conf',
                            '/etc/php/5.5/fpm/pool.d/www.conf',
                            '/etc/php/5.6/fpm/pool.d/www.conf'
                            ]
        phpfpm_bin_list = ['/usr/sbin/php-fpm',
                           '/usr/sbin/php5-fpm',
                           '/usr/sbin/php-fpm5.3',
                           '/usr/sbin/php-fpm5.5',
                           '/usr/sbin/php-fpm5.6'
                           ]
        # First check php-fpm config and binary file from process,
        #   if process is not running, then check from the list above
        rc, out, err = utils.execute("ps -U root|egrep 'php5?\.?[3-6]?-fpm'|grep -v 'grep'|awk '{print $1}'")
        if rc != 0 or out.strip() == '':
            for conf in phpfpm_conf_list:
                if os.path.exists(conf):
                    phpfpm_config_path = conf
                    break
            for phpbin in phpfpm_bin_list:
                if os.path.exists(phpbin):
                    phpfpm_bin = phpbin
                    break
        else:
            p = psutil.Process(int(out.strip()))
            phpfpm_bin = p.exe()
            try:
                if p.cmdline()[0].find('php-fpm.conf') >= 0:
                    phpfpm_config_path = p.cmdline()[0].split('(')[1].strip(')')
            except IndexError:
                pass
        # convert php-fpm.conf to www.conf
        if phpfpm_config_path is not None and phpfpm_config_path != '' and os.path.isfile(phpfpm_config_path) and \
                not phpfpm_config_path.endswith('www.conf'):
            phpfpm_dir = os.path.dirname(phpfpm_config_path)
            if os.path.isfile(os.path.join(phpfpm_dir, 'php-fpm.d/www.conf')):
                phpfpm_config_path = os.path.join(phpfpm_dir, 'php-fpm.d/www.conf')
            elif os.path.isfile(os.path.join(phpfpm_dir, 'pool.d/www.conf')):
                phpfpm_config_path = os.path.join(phpfpm_dir, 'pool.d/www.conf')
            else:
                phpfpm_config_path = None
        # If couldn't get config and binary file above, first try "php-fpm",
        #   If still failed, then ask customer input manually
        if phpfpm_bin == '' or phpfpm_bin is None:
            phpfpm_bin = 'php-fpm'
        while True:
            if utils.executable(phpfpm_bin):
                break
            else:
                utils.out(utils.print_str("WRONG_SERVICE_BIN_PATH", Phpfpm.getname()))
                phpfpm_bin = utils.prompt(utils.print_str("SERVICE_BIN_PATH", Phpfpm.getname()))
                continue
        while True:
            if phpfpm_config_path is None or phpfpm_config_path == '' or not os.path.isfile(phpfpm_config_path) \
                    or not phpfpm_config_path.endswith('.conf'):
                utils.out(utils.print_str("WRONG_SERVICE_CONFIG_PATH", Phpfpm.getname()))
                phpfpm_config_path = utils.prompt(utils.print_str("SERVICE_CONFIG_PATH", Phpfpm.getname(), '[www.conf]'))
                continue
            else:
                break
        # Fetch service name from systemd or init.d folder depends on OS
        if (system.distribution == "centos" and system.version.startswith("7.")) \
            or (system.distribution == "redhat" and system.version.startswith("7.")):
            systemd = "/usr/lib/systemd/system/"
            files = os.listdir(systemd)
            for file in files:
                if os.path.isfile(os.path.join(systemd, file)) and re.match('php.*?-fpm.service', file):
                    phpfpm_service_name = file.replace('.service', '').strip()
                    break
        else:
            init_folder = "/etc/init.d/"
            files = os.listdir(init_folder)
            for file in files:
                if os.path.isfile(os.path.join(init_folder, file)) and re.match('php.*?-fpm', file):
                    phpfpm_service_name = file.strip()
                    break
        if phpfpm_service_name is None or phpfpm_service_name == '':
            phpfpm_service_name = utils.prompt(utils.print_str("SERVICE_NAME", Phpfpm.getname()))
        if phpfpm_bin != '' and phpfpm_config_path != '' and phpfpm_service_name != '':
            result = True
        pars['phpfpm_bin_path'] = phpfpm_bin
        pars['phpfpm_conf_path'] = phpfpm_config_path
        pars['phpfpm_service_name'] = phpfpm_service_name
        return result, pars

    @staticmethod
    def configure(system):
        phpfpm_restart = "false"
        phpfpm_start = "false"
        result, pars = Phpfpm.getconf(system)
        if not result:
            utils.out(utils.print_str("NOT_DETECT_CONF_PATH", Phpfpm.getname()))
            utils.out(utils.print_str("MANUALLY_CONFIGURE"), Phpfpm.getname())
            return
        if system.is_proc_running("php5?\.?[3-6]?-fpm"):
            if utils.confirm(utils.print_str("RESTART_SERVICE", Phpfpm.getname())):
                phpfpm_restart = "true"
            else:
                utils.out_progress_info(utils.print_str("RESTART_SERVICE_LATER", Phpfpm.getname()))
        else:
            if utils.confirm(utils.print_str("START_SERVICE", Phpfpm.getname())):
                phpfpm_start = "true"
            else:
                utils.out_progress_info(utils.print_str("START_SERVICE_LATER", Phpfpm.getname()))
        pars['phpfpm_restart'] = phpfpm_restart
        pars['phpfpm_start'] = phpfpm_start
        pars_json = json.dumps(pars)
        utils.out_progress_wait(utils.print_str("CONFIGURE_MONITOR", Phpfpm.getname()))
        rc, out, err = utils.ansible_play("phpfpm_monitoring", pars_json)
        if rc == 0:
            utils.out_progress_done()
        else:
            utils.out_progress_fail()
            utils.err(utils.print_str("FAILED_CONFIGURE_MONITOR", Phpfpm.getname()))

