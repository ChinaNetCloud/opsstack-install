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
        if system.os == 'linux':
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
        mysql_root_pass = ''
        port = None
        rc, out, err = utils.execute(
            "ss -ntlp -A inet | grep mysqld |awk '{print $5}'|awk -F: '{print $NF}'|head -1")
        if rc != 0 or out.strip() == '':
            out_info = utils.print_str("FAILED_GET_LISTEN_PORT", MySQL.getname())
            utils.out(out_info)
            port = 3306
        else:
            port = out.strip()
        confirm_slave_str = utils.print_str("SLAVE_CHECK", MySQL.getname(), port)
        slave_confirmation = utils.confirm(confirm_slave_str)
        if slave_confirmation is True:
            pars['slave'] = True
            return pars
        else:
            pars['slave'] = False
        user = utils.prompt(utils.print_str("MYSQL_USER"))
        if user == '':
            user = 'root'
        passwd = utils.prompt_pass(utils.print_str("MYSQL_USER_PASSWD", port, user))
        if passwd != '':
            mysql_root_pass = passwd
        pars['user'] = user
        pars['mysql_root_pass'] = mysql_root_pass
        pars['mysql_port'] = port
        pars['mysql_nccheckdb_pass'] = MySQL.generate_passwd()
        return pars

    @staticmethod
    def configure(system):
        confirm_str = utils.print_str("CREATE_MONITOR_USER", MySQL.getname())
        confirmation = utils.confirm(confirm_str)
        if confirmation is False:
            utils.out(utils.print_str("Zabbix_Monitoring_User_Required", MySQL.getname()))
            utils.out(utils.print_str("CREATE_USER_DOC", MySQL.getname()))
            return True
        pars = MySQL.get_pars()
        if pars['slave'] is True:
            utils.out(utils.print_str("SLAVE_SKIP", MySQL.getname()))
            utils.out(utils.print_str("CREATE_USER_DOC", MySQL.getname()))
            return True
        # Create .my.cnf file to connect mysql
        pars['mycnf_file'] = "/tmp/.ansible_my_cnf"
        with open(pars['mycnf_file'], 'w') as mycnf:
            mycnf.write("[client]\n")
            mycnf.write("user=%s\n" % pars['user'])
            mycnf.write("password=%s\n" % pars['mysql_root_pass'])
            mycnf.write("port=%s" % pars['mysql_port'])
        utils.out_progress_wait(utils.print_str("CONFIGURE_DATABASE_MONITOR", MySQL.getname(), pars['mysql_port']))
        del pars['mysql_root_pass'], pars['user'], pars['mysql_port']
        pars_json = json.dumps(pars)
        rc, out, err = utils.ansible_play("mysql_monitoring", pars_json)
        if rc != 0:
            utils.out_progress_fail()
            utils.err(utils.print_str("FAILED_CREATE_USER", MySQL.getname()))
            exit(1)
        else:
            utils.out_progress_done()




