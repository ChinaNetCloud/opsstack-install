import abstract


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
                result = True
        return result

    @staticmethod
    def configure(system):
        return True

