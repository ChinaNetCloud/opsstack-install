class Abstract(object):
    def check_compatibility(self):
        raise NotImplementedError("Should have implemented this")

    def configure(self):
        # 1. Setup environment
        self._setup_environemt()
        # 2. Service discovery
        self._service_discovery()
        # 3. Prompt for details
        self._collect_information()
        # 4. Pre-register with OpsStack
        self._register_server()
        # 5. Install monitoring
        self._install_monitoring()
        # 6. Run setup for discovered services
        self._configure_service_monitoring()

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

    def is_app_installed(self, app_name):
        raise NotImplementedError("Should have implemented this")

    def is_proc_running(self, proc_name):
        raise NotImplementedError("Should have implemented this")

    def is_port_free(self, port_number):
        raise NotImplementedError("Should have implemented this")
