import abstract
from random import choice
import string
import json
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
        if system.os == 'linux':
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
            utils.out(utils.print_str("Zabbix_Monitoring_User_Required", MongoDB.getname()))
            utils.out(utils.print_str("CREATE_USER_DOC", MongoDB.getname()))
            exit(1)
        user = utils.prompt(utils.print_str("MONGO_ADMIN_USER", port))
        passwd = utils.prompt_pass(utils.print_str("MONGO_ADMIN_PASS", port))
        if user != '':
            mongo_admin_user = user
        if passwd != '':
            mongo_admin_passwd = passwd
        pars['user'] = mongo_admin_user
        pars['passwd'] = mongo_admin_passwd
        pars['port'] = port
        pars['nccheckdb_pwd'] = MongoDB.generate_passwd()
        return pars

    @staticmethod
    def configure(system):
        pars = MongoDB.get_pars()
        pars_json = json.dumps(pars)
        utils.out_progress_wait(utils.print_str("CONFIGURE_DATABASE_MONITOR", MongoDB.getname(), pars['port']))
        if not system.config.get("mongo_monitoring_configured") == "yes":
            rc, out, err = utils.ansible_play("rhel_mongo_monitoring", pars_json)
        if rc != 0:
            utils.out_progress_fail()
            utils.err(utils.print_str("FAILED_CREATE_USER", MongoDB.getname()))
            exit(1)
        else:
            with open('/home/zabbix/conf/nc_mongo_check.conf', 'w') as mongo_conf:
                mongo_conf.write('MONGO_USER="nccheckdb"\n')
                mongo_conf.write('MONGO_PWD="%s"\n' % pars['nccheckdb_pwd'])
                mongo_conf.write('MONGO_HOST="localhost"\n')
                mongo_conf.write('MONGO_PORT="%s"' % pars['port'])
            utils.out_progress_done()



