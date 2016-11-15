import abstract
import os
import re
import psutil
import json

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
        if system.os == 'linux':
            if system.is_proc_running("nginx") or system.is_app_installed("nginx"):
                result = True
        return result

    @staticmethod
    def getconf(system):
        result = False
        conf_file = None
        pars = {}
        rc, out, err = utils.execute("ps -U root|grep nginx|grep -v 'grep'|awk '{print $1}'")
        if rc != 0 or out == '':
            # If nginx is not running, use "nginx" as the binary path by default
            bin_path = "nginx"
        else:
            p = psutil.Process(int(out.strip()))
            bin_path = p.exe()
        # Make sure binary file is executable
        while True:
            command_rc, command_out, command_err = utils.execute('command -V ' + bin_path)
            if command_rc == 0:
                break
            else:
                utils.out(utils.print_str("WRONG_SERVICE_BIN_PATH", Nginx.getname()))
                bin_path = utils.prompt(utils.print_str("SERVICE_BIN_PATH", Nginx.getname()))
                continue
        # Get build parameters of nginx
        parse_rc, parse_out, parse_err = utils.execute(bin_path + ' -V')
        if parse_rc == 0 and parse_err != "":
            for i in parse_err.split(' '):
                if re.match(r"\-\-conf\-path\=.*\.conf", i):
                    conf_file = i.split('=')[1]
                    break
        # If we couldn't parse the config path, ask customer to input the config path
        while True:
            if conf_file is None or conf_file == '' or not os.path.isfile(conf_file) or not conf_file.endswith('.conf'):
                utils.out(utils.print_str("WRONG_SERVICE_CONF_PATH", Nginx.getname()))
                conf_file = utils.prompt(utils.print_str("SERVICE_CONFIG_PATH", Nginx.getname(), '[nginx.conf]'))
                continue
            else:
                conf_dir = os.path.dirname(conf_file)
                result = True
                break
        pars['nginx_conf_file'] = conf_file
        pars['nginx_conf_dir'] = conf_dir
        pars['nginx_bin_path'] = bin_path
        return result, pars

    @staticmethod
    def configure(system):
        nginx_restart = "false"
        nginx_start = "false"
        result, pars = Nginx.getconf(system)
        if not result:
            utils.out(utils.print_str("NOT_DETECT_CONF_PATH", Nginx.getname()))
            utils.out(utils.print_str("MANUALLY_CONFIGURE"), Nginx.getname())
            return
        if system.is_proc_running("nginx"):
            if utils.confirm(utils.print_str("RESTART_SERVICE", Nginx.getname())):
                nginx_restart = "true"
            else:
                utils.out_progress_info(utils.print_str("RESTART_SERVICE_LATER", Nginx.getname()))
        else:
            if utils.confirm(utils.print_str("START_SERVICE", Nginx.getname())):
                nginx_start = "true"
            else:
                utils.out_progress_info(utils.print_str("START_SERVICE_LATER", Nginx.getname()))
        pars['nginx_restart'] = nginx_restart
        pars['nginx_start'] = nginx_start
        pars_json = json.dumps(pars)
        utils.out_progress_wait(utils.print_str("CONFIGURE_MONITOR", Nginx.getname()))
        rc, out, err = utils.ansible_play("nginx_monitoring", pars_json)
        if rc == 0:
            utils.out_progress_done()
        else:
            utils.out_progress_fail()
            utils.err(utils.print_str("FAILED_CONFIGURE_MONITOR", Nginx.getname()))
