import abstract
from lib import utils

from tempfile import mkstemp
from shutil import move
from os import remove, close, chmod, chown
from os.path import exists
import re
import stat
import pwd


class Redis(abstract.Abstract):
    def __init__(self):
        abstract.Abstract.__init__(self)

    @staticmethod
    def getname():
        return 'redis'

    @staticmethod
    def discover(system):
        result = False
        if system.os == 'linux':
            if system.is_proc_running("redis"):
                rc, out, err = utils.execute('''ss -ntpl -A inet|grep "redis"''')
                if rc == 0:
                    result = True
        return result

    @staticmethod
    def get_pars():
        pars = {}
        # port = None
        rc, out, err = utils.execute(
            "ss -ntlp -A inet | grep redis |awk '{print $5}'|head -1")
        if rc != 0 or out.strip() == '':
            out_info = utils.print_str("FAILED_GET_LISTEN_PORT", Redis.getname())
            utils.err(out_info)
        else:
            host = out.split(':')[-2]
            port = out.split(':')[-1].rstrip()
        pars['redis_host'] = host
        pars['redis_port'] = port
        return pars

    @staticmethod
    def configure(system):
        pars = Redis.get_pars()

        # cat /tmp/.ansible_redis_cnf << EOF
        # > redis_auth_pass
        # > EOF
        redis_config_file = '/tmp/.ansible_redis_cnf'
        redis_auth_pass = ''
        if utils.batch_install_tag():
            if not exists(redis_config_file):
                utils.out_progress_wait(utils.print_str("CONFIGURE_DATABASE_MONITOR", Redis.getname(), pars['redis_port']))
                utils.out_progress_fail()
                utils.err(utils.print_str("CAN_NOT_FOUND_CNF", Redis.getname()))
            else:
                f1 = open(redis_config_file, 'r')
                if len(f1.readlines()) > 0:
                    f1.seek(0)
                    redis_auth_pass = f1.readlines()[0].split('\n')[0].strip()
                f1.close()
        else:
            redis_auth_pass = utils.prompt_pass(utils.print_str("REDIS_AUTH_PASSWD", pars['redis_port']))

        utils.out_progress_wait(utils.print_str("CONFIGURE_DATABASE_MONITOR", Redis.getname(), pars['redis_port']))
        try:
            # update redis_check.conf file to connect redis
            file_path = "/var/lib/nc_zabbix/conf/nc_redis_check.conf"
            host_str = 'REDIS_IP="' + pars['redis_host'] + '"'
            passwd_str = 'REDIS_PASSWD="' + redis_auth_pass + '"'
            fh, abs_path = mkstemp()
            with open(abs_path, 'w') as new_file:
                with open(file_path) as old_file:
                    for line in old_file:
                        if re.search('REDIS_PASSWD=.*', line):
                            new_file.write(re.sub('REDIS_PASSWD=.*', passwd_str, line))
                            continue
                        if re.search('#REDIS_IP=.*', line):
                            new_file.write(re.sub('#REDIS_IP=.*', host_str, line))
                            continue
                        new_file.write(line)
            close(fh)
            # Remove original file
            remove(file_path)

            # Move new file
            move(abs_path, file_path)
            # Change the  owner and permission of redis.conf file
            chmod(file_path, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP)
            chown(file_path, pwd.getpwnam('nc-zabbix').pw_uid, pwd.getpwnam('nc-zabbix').pw_gid)
            utils.out_progress_done()
        except Exception as e:
            utils.out_progress_fail()
            utils.err(utils.print_str("FAILED_CONFIGURE_MONITOR", Redis.getname()))
            raise Exception(e)
