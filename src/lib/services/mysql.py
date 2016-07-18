import abstract
import os
import re
import getpass
from random import choice
import string

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
    def configure(system):
        if not utils.confirm("CREATE_MONITOR_USER?"):
            utils.out_progress_skip()
            return False
        nccheckdb_passwd = MySQL.generate_passwd()
        with open('/home/zabbix/conf/mysql_credentials', 'w') as mysql_file:
            mysql_file.write('[client]\n')
            mysql_file.write('user=nccheckdb\n')
            mysql_file.write('password=%s\n' % nccheckdb_passwd)
            mysql_file.write('host=localhost')
        rc, out, err = utils.execute("ss -ntlp -A inet | awk -F: '/mysql/&&/LISTEN/{print $2}' | awk '{print $1}'")
        if rc != 0 or out == '':
            utils.out_progress_fail()
            utils.err("Failed to get mysql listening port")
            exit(1)
        for port in out.strip().split('\n'):
            mysql_root = getpass.getpass("%s_MYSQL_ROOT_PASSWD:" % port)
            utils.out_progress_wait("CONFIGURE_MYSQL_%s_MONITOR" % port)
            mysql_cmd = "mysql -N -uroot -p" + mysql_root + " -P " + port
            utils.execute(mysql_cmd +
                          ''' -e "CREATE USER 'nccheckdb'@'localhost' IDENTIFIED BY '%s'"''' %(nccheckdb_passwd))
            utils.execute(mysql_cmd +
                          ''' -e "CREATE USER 'nccheckdb'@'127.0.0.1' IDENTIFIED BY '%s'"''' %(nccheckdb_passwd))
            utils.execute(mysql_cmd +
                          ''' -e "GRANT PROCESS, REPLICATION CLIENT on *.* TO 'nccheckdb'@'localhost'"''')
            utils.execute(mysql_cmd +
                          ''' -e "GRANT SELECT (Select_priv) ON mysql.user TO 'nccheckdb'@'localhost'"''')
            utils.execute(mysql_cmd +
                          ''' -e "GRANT PROCESS, REPLICATION CLIENT on *.* TO 'nccheckdb'@'127.0.0.1'"''')
            utils.execute(mysql_cmd +
                          ''' -e "GRANT SELECT (Select_priv) ON mysql.user TO 'nccheckdb'@'127.0.0.1'"''')
            utils.execute(mysql_cmd + ''' -e "flush privileges"''')
            utils.out_progress_done()