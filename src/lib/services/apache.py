import abstract
import os
import re
import psutil
import json

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
        if system.distribution == 'centos' or system.distribution == 'redhat' or system.distribution == 'amazon':
            if system.is_proc_running("httpd") or system.is_app_installed("httpd"):
                result = True
        elif system.distribution == 'ubuntu' or system.distribution == 'debian':
            if system.is_proc_running("apache2") or system.is_app_installed("apache2"):
                result = True
        return result

    @staticmethod
    def getconf(system):
        result = False
        httpd_conf = None
        httpd_dir = None
        httpd_running = "false"
        pars = {}
        if system.distribution == 'centos' or system.distribution == 'redhat' or system.distribution == 'amazon':
            # Set default binary file in case service is not running
            bin_path = "httpd"
            service_name = "httpd"
        else:
            # Set default binary file in case service is not running
            bin_path = "apache2"
            service_name = "apache2"
        rc, out, err = utils.execute("ps -U root|grep %s|grep -v 'grep'|awk '{print $1}'" % service_name)
        if rc == 0 and out != '':
            p = psutil.Process(int(out.strip()))
            bin_path = p.exe()
            httpd_running = "true"
            try:
                if p.cmdline()[0].find('httpd.conf') >= 0 or p.cmdline()[0].find('apache2.conf') >= 0:
                    if re.search(r'(/[^\s\t\n\r]*/httpd\.conf)', p.cmdline()[0]):
                        conf_file = re.search(r'(/[^\s\t\n\r]*/httpd\.conf)', p.cmdline()[0]).group(1)
                    elif re.search(r'(/[^\s\t\n\r]*/apache2\.conf)', p.cmdline()[0]):
                        conf_file = re.search(r'(/[^\s\t\n\r]*/apache2\.conf)', p.cmdline()[0]).group(1)
                    if os.path.isfile(conf_file):
                        httpd_conf = conf_file
            except Exception as e:
                pass
        # Make sure binary file is executable
        while True:
            if utils.executable(bin_path):
                break
            else:
                utils.out(utils.print_str("WRONG_SERVICE_CONF_PATH", Apache.getname()))
                bin_path = utils.prompt(utils.print_str("SERVICE_BIN_PATH", Apache.getname()))
                continue
        # Get build parameters of apache
        if conf_file is None or conf_file == '' or not os.path.isfile(conf_file) or not conf_file.endswith('.conf'):
            parse_rc, parse_out, parse_err = utils.execute(bin_path + ' -V')
            if parse_rc == 0 and parse_out != "":
                for line in parse_out.splitlines():
                    if re.search(r'(HTTPD_ROOT=\".*\")', line):
                        conf_dir = re.search(r'(HTTPD_ROOT=\".*\")', line).group(1).split("=")[1].strip('\"\'')
                    elif re.search(r'(SERVER_CONFIG_FILE=\".*\")', line):
                        conf_file = re.search(r'(SERVER_CONFIG_FILE=\".*\")', line).group(1).split("=")[1].strip('\"\'')
                if conf_dir != "" and conf_file != "" and conf_dir.startswith('/') and conf_file.endswith('.conf') \
                        and os.path.isfile(os.path.join(conf_dir, conf_file)):
                    httpd_conf = os.path.join(conf_dir, conf_file)
        # If we couldn't get apache config file above then ask customer to input it manually
        while True:
            if httpd_conf is None or httpd_conf == '' or not os.path.isfile(httpd_conf) or not httpd_conf.endswith('.conf'):
                utils.out(utils.print_str("WRONG_SERVICE_CONFIG_PATH", Apache.getname()))
                httpd_conf = utils.prompt(utils.print_str("SERVICE_CONFIG_PATH", Apache.getname(), '[apache2.conf/httpd.conf]'))
                continue
            else:
                httpd_dir = os.path.dirname(httpd_conf)
                result = True
                break
        pars['httpd_bin'] = bin_path
        pars['httpd_conf'] = httpd_conf
        pars['httpd_dir'] = httpd_dir
        pars['service_name'] = service_name
        pars['httpd_running'] = httpd_running
        return result, pars

    @staticmethod
    def configure(system):
        httpd_restart = "false"
        httpd_start = "false"
        result, pars = Apache.getconf(system)
        if not result:
            utils.out(utils.print_str("NOT_DETECT_CONF_PATH", Apache.getname()))
            utils.out(utils.print_str("MANUALLY_CONFIGURE"), Apache.getname())
            return
        if pars['httpd_running'] == "true":
            if utils.confirm(utils.print_str("RESTART_SERVICE", Apache.getname())):
                httpd_restart = "true"
            else:
                utils.out_progress_info(utils.print_str("RESTART_SERVICE_LATER", Apache.getname()))
        else:
            if utils.confirm(utils.print_str("START_SERVICE", Apache.getname())):
                httpd_start = "true"
            else:
                utils.out_progress_info(utils.print_str("START_SERVICE_LATER", Apache.getname()))
        pars['httpd_restart'] = httpd_restart
        pars['httpd_start'] = httpd_start
        pars_json = json.dumps(pars)
        utils.out_progress_wait(utils.print_str("CONFIGURE_MONITOR", Apache.getname()))
        rc, out, err = utils.ansible_play("apache_monitoring", pars_json)
        if rc == 0:
            utils.out_progress_done()
        else:
            utils.out_progress_fail()
            utils.err(utils.print_str("FAILED_CONFIGURE_MONITOR", Apache.getname()))
