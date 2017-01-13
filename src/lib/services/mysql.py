import abstract
from random import choice
import string
import json
import os
from lib import log

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
                rc, out, err = utils.execute('''ss -ntpl -A inet|grep "mysqld"''')
                if rc == 0:
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
        rc, out, err = utils.execute("mysql --version | awk -F'Distrib |,' '{print $2}'")
        if rc != 0 or out.strip() == '':
            utils.err("FAILED_GET_MYSQL_VERSION")
        else:
            if out.startswith('5.6.'):
                pars['enable_sys'] = 'Need'
            elif out.startswith('5.7.'):
                pars['enable_sys'] = 'NO Need'
            else:
                pars['enable_sys'] = 'NOT Support'

        rc, out, err = utils.execute(
            "ss -ntlp -A inet | grep mysqld |awk '{print $5}'|awk -F: '{print $NF}'|head -1")
        if rc != 0 or out.strip() == '':
            out_info = utils.print_str("FAILED_GET_LISTEN_PORT", MySQL.getname())
            utils.out(out_info)
            port = 3306
        else:
            port = out.strip()

        config_file = '/tmp/.ansible_my_cnf'
        if utils.batch_install_tag():
            if not os.path.exists(config_file):
                utils.out_progress_wait(utils.print_str("CONFIGURE_DATABASE_MONITOR", MySQL.getname(), port))
                utils.out_progress_fail()
                utils.err(utils.print_str("CAN_NOT_FOUND_CNF", MySQL.getname()))
            else:
                pars['mycnf_file'] = "/tmp/.ansible_my_cnf"
                mysql_conn = "mysql --defaults-extra-file=%s" % config_file
                slave_cmd = "echo 'show slave status \G' | %s " % mysql_conn
                rc1, out1, err1 = utils.execute(slave_cmd)
                if rc1 == 0 and out1.find('Slave_SQL_Running') != -1:
                    pars['slave'] = True
                    return pars
                else:
                    pars['slave'] = False
        else:
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
        # Create .my.cnf file to connect mysql if not batch-install.
        if not utils.batch_install_tag():
            pars['mycnf_file'] = "/tmp/.ansible_my_cnf"
            with open(pars['mycnf_file'], 'w') as mycnf:
                mycnf.write("[client]\n")
                mycnf.write("user=%s\n" % pars['user'])
                mycnf.write("password=%s\n" % pars['mysql_root_pass'])
                mycnf.write("host=localhost\n")
                mycnf.write("port=%s" % pars['mysql_port'])
        utils.out_progress_wait(utils.print_str("CONFIGURE_DATABASE_MONITOR", MySQL.getname(), pars['mysql_port']))
        # Check slow log path as rsyslog requires
        MySQL.slow_log(pars['mycnf_file'])

        # remove some key
        pars.pop("mysql_root_pass", None)
        pars.pop("user", None)
        pars.pop("slave", None)
        pars_json = json.dumps(pars)
        rc, out, err = utils.ansible_play("mysql_monitoring", pars_json)

        if rc != 0:
            utils.out_progress_fail()
            utils.err(utils.print_str("FAILED_CREATE_USER", MySQL.getname()))
        else:
            utils.out_progress_done()

    @staticmethod
    def slow_log(config_file):
        mysql_conn = "mysql --defaults-extra-file=%s" % config_file
        status_cmd = "echo 'SHOW VARIABLES WHERE variable_name = \"slow_query_log\"' | %s | awk '/slow_query_log/{print $2}'" % mysql_conn
        path_cmd = "echo 'SHOW VARIABLES WHERE variable_name = \"slow_query_log_file\"' | %s | awk '/slow_query_log_file/{print $2}'" % mysql_conn
        dir_cmd = "echo 'SHOW VARIABLES WHERE variable_name = \"datadir\"' | %s | awk '/datadir/{print $2}'" % mysql_conn
        rc1, out1, err1 = utils.execute(status_cmd)
        # Check if slow log is turned on
        if rc1 == 0 and out1.strip().lower() == 'on':
            rc2, out2, err2 = utils.execute(path_cmd)
            if rc2 == 0 and out2.strip().startswith('/') and os.path.isfile(out2.strip()):
                os.environ['MYSQL_SLOW_LOG_PATH'] = out2.strip()
            else:
                rc3, out3, err3 = utils.execute(dir_cmd)
                if rc3 == 0 and os.path.isdir(out3.strip()):
                    os.environ['MYSQL_SLOW_LOG_PATH'] = os.path.join(out3.strip(), out2.strip())
        # If failed to connect to mysql, then log the errmsg
        elif rc1 != 0:
            log.get_logger().debug("Couldn't detect slow log path, see error below:")
            log.get_logger().debug(err1)

