import abstract
from random import choice
import string
import json

from lib import utils

class MySQL(abstract.Abstract):
    def __init__(self):
        abstract.Abstract.__init__(self)

    @staticmethod
    def getname():
        return 'mysql'

    @staticmethod
    def discover(system):
        result = False
        if system.OS == 'linux':
            if system.is_proc_running("mysqld"):
                result = True
        return result

    @staticmethod
    def generate_passwd():
        passwd_length = 12
        passwd_seed = string.digits + string.ascii_letters
        passwd = []
        while (len(passwd) < passwd_length):
            passwd.append(choice(passwd_seed))
        return ''.join(passwd)

    @staticmethod
    def get_pars():
        pars = {}
        mysql_root_pass = None
        port = None
        rc, out, err = utils.execute(
            "ss -ntlp -A inet | awk -F: '/mysqld/&&/LISTEN/{print $2}' | awk '{print $1}'| sort | head -1")
        if rc != 0 or out.strip() == '':
            out_info = utils.print_str("FAILED_GET_LISTEN_PORT", MySQL.getname())
            utils.out(out_info)
            port = 3306
        else:
            port = out.strip()
        confirm_str = utils.print_str("CREATE_MONITOR_USER", MySQL.getname())
        confirmation = utils.confirm(confirm_str)
        if confirmation is False:
            utils.out(utils.print_str("Zabbix_Monitoring_User_Required", MySQL.getname()))
            utils.out(utils.print_str("CREATE_USER_DOC", MySQL.getname()))
            exit(1)
        confirm_slave_str = utils.print_str("SLAVE_CHECK", MySQL.getname(), port)
        slave_confirmation = utils.confirm(confirm_slave_str)
        if slave_confirmation is True:
            utils.out(utils.print_str("SLAVE_SKIP", MySQL.getname()))
            utils.out(utils.print_str("CREATE_USER_DOC", MySQL.getname()))
            pars['slave'] = True
            return pars
        else:
            pars['slave'] = False
        passwd = utils.prompt_pass(utils.print_str("MYSQL_ROOT_PASSWD: ", port))
        if passwd != '':
            mysql_root_pass = passwd
        pars['user'] = 'root'
        pars['mysql_root_pass'] = mysql_root_pass
        pars['mysql_port'] = port
        pars['mysql_nccheckdb_pass'] = MySQL.generate_passwd()
        return pars

    @staticmethod
    def configure(system):
        if not system.config.get("mysql_monitoring_configured") == "yes":
            pars = MySQL.get_pars()
            if pars['slave'] is True:
                system.config.set("mysql_monitoring_configured", "yes")
                return True
            pars_json = json.dumps(pars)
            utils.out_progress_wait(utils.print_str("CONFIGURE_DATABASE_MONITOR", MySQL.getname(), pars['mysql_port']))
            rc, out, err = utils.ansible_play("rhel_mysql_monitoring", pars_json)
            if rc != 0:
                utils.out_progress_fail()
                utils.err(utils.print_str("FAILED_CREATE_USER", MySQL.getname()))
                exit(1)
            else:
                system.config.set("mysql_monitoring_configured", "yes")
                utils.out_progress_done()
        else:
            utils.out_progress_skip()



