class Abstract(object):
    def check_compatibility(self):
        raise NotImplementedError("Should have implemented this")

    def configure(self):
        raise NotImplementedError("Should have implemented this")

    def is_app_installed(self, app_name):
        raise NotImplementedError("Should have implemented this")

    def is_proc_running(self, proc_name):
        raise NotImplementedError("Should have implemented this")

    def is_port_free(self, port_number):
        raise NotImplementedError("Should have implemented this")
