class Abstract(object):

    def init(self):
        raise NotImplementedError("Should have implemented this")

    def _verify_permissions(self):
        raise NotImplementedError("Should have implemented this")

    def _collect_facts(self):
        raise NotImplementedError("Should have implemented this")

    def _check_compatibility(self):
        raise NotImplementedError("Should have implemented this")

    def _setup_environemt(self):
        raise NotImplementedError("Should have implemented this")

    def _service_discovery(self):
        raise NotImplementedError("Should have implemented this")

    def _collect_information(self):
        raise NotImplementedError("Should have implemented this")

    def _register_server(self):
        raise NotImplementedError("Should have implemented this")

    def _install_monitoring(self):
        raise NotImplementedError("Should have implemented this")

    def _configure_service_monitoring(self):
        raise NotImplementedError("Should have implemented this")

    def _is_app_installed(self, app_name):
        raise NotImplementedError("Should have implemented this")

    def _is_proc_running(self, proc_name):
        raise NotImplementedError("Should have implemented this")

    def _is_port_free(self, port_number):
        raise NotImplementedError("Should have implemented this")
