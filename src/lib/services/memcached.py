import abstract
from lib import utils


class Memcached(abstract.Abstract):
    def __init__(self):
        abstract.Abstract.__init__(self)

    @staticmethod
    def getname():
        return 'memcached'

    @staticmethod
    def discover(system):
        result = False
        if system.os == 'linux':
            if system.is_proc_running("memcached"):
                rc, out, err = utils.execute('''ss -ntpl -A inet|grep "redis"''')
                if rc == 0:
                    result = True
        return result

    @staticmethod
    def configure(system):
        return True

