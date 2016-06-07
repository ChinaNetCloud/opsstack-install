import abstract


class Nginx(abstract.Abstract):
    def __init__(self):
        abstract.Abstract.__init__(self)

    @staticmethod
    def getname():
        return 'nginx'

    @staticmethod
    def discover(system):
        result = False
        if system.OS == 'linux':
            if system.is_proc_running("nginx") or system.is_app_installed("nginx"):
                result = True
        return result

    @staticmethod
    def configure(system):
        print("Configuring %s" % Nginx.getname())
