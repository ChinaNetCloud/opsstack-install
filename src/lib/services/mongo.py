import abstract
from random import choice
import string

from lib import utils

class MongoDB(abstract.Abstract):
    def __init__(self):
        abstract.Abstract.__init__(self)

    @staticmethod
    def getname():
        return 'MongoDB'

    @staticmethod
    def discover(system):
        result = False
        if system.OS == 'linux':
            if system.is_proc_running("mongod"):
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
    def get_pars(mongo_admin_user=None, mongo_admin_passwd=None):
        pars = {}
        rc, out, err = utils.execute(
            "ss -ntlp -A inet | awk -F: '/mongod/&&/LISTEN/{print $2}' | awk '{print $1}'|head -1")
        if rc != 0 or out == '':
            err_info = utils.print_str("FAILED_GET_LISTEN_PORT", MongoDB.getname())
            utils.err(err_info)
            exit(1)
        else:
            port = out.strip()
        confirm_str = utils.print_str("CREATE_MONITOR_USER", MongoDB.getname())
        confirmation = utils.confirm(confirm_str)
        if confirmation is False:
            utils.out("Zabbix Monitoring User Is Required." % MongoDB.getname())
            utils.out("CREATE_MON_USER_DOC")
            exit(1)
        user = getpass.getpass("%s_Mongo_AdminDB_User:" % port)
        passwd = getpass.getpass("%s_Mongo_AdminDB_Passwd:" % port)
        if user != '':
            mongo_admin_user = user
        if passwd != '':
            mongo_admin_passwd = passwd
        pars['user'] = mongo_admin_user
        pars['passwd'] = mongo_admin_passwd
        pars['port'] = port
        pars['nccheckdb'] = MongoDB.generate_passwd()
        return pars

    @staticmethod
    def configure(system):
        pars = MongoDB.get_pars()
        utils.out_progress_wait("CONFIGURE_%s_MONITOR" % MongoDB.getname())
        if pars['user'] is None and pars['passwd'] is None:
            mongo_conn_cmd = "/usr/bin/mongo admin --port %s --quiet" % pars['port']
        else:
            mongo_conn_cmd = "/usr/bin/mongo admin -u %s -p %s --port %s --quiet" % (pars['user'], pars['passwd'], pars['port'])
        rc, out, err = utils.execute(mongo_conn_cmd + ''' --eval "db.isMaster()['ismaster']"''')
        if rc != 0 or out == "":
            utils.out_progress_fail()
            utils.err("Falied to connect to %s !" % MongoDB.getname())
            exit(1)
        elif out.strip() == "false":
            utils.out_progress_skip()
            utils.out("This is a slave instance, please refer to CNC Documentation to configure monitoring")
            return False
        rc1, out1, err1 = utils.execute(mongo_conn_cmd + ''' --eval "db.getUser('nccheckdb')"''')
        if out1.strip() != "null":
            utils.out_progress_skip()
            utils.out("Mongo monitoring user \'nccheckdb\' already exist")
            return True
        else:
            rc2, out2, err2 = utils.execute(mongo_conn_cmd + ''' --eval "
                                            db.createUser({
                                                user: 'nccheckdb',
                                                pwd: '%s',
                                                roles: [{
                                                  'role': 'read',
                                                  'db': 'admin'
                                                  }]
                                              })"''' % pars['nccheckdb'])
        if rc2 != 0:
            utils.out_progress_fail()
            utils.err("Falied to create monitoring user for %s !" % MongoDB.getname())
            exit(1)
        else:
            with open('/home/zabbix/conf/nc_mongo_check.conf', 'w') as mongo_conf:
                mongo_conf.write('MONGO_USER="nccheckdb"\n')
                mongo_conf.write('MONGO_PWD="%s"\n' % pars['nccheckdb'])
                mongo_conf.write('MONGO_HOST="localhost"\n')
                mongo_conf.write('MONGO_PORT="%s"' % pars['port'])
            utils.out_progress_done()



