import socket

from abstract import Abstract

from lib import utils
from lib import config


class System(Abstract):
    def __init__(self):
        self.config = config.get_config()

        self.os = "linux"
        self.os_name = "centos"
        self.os_version = "7"

        self.is_ansible_present = None
        self.is_pip_present = None
        self.is_easy_install_present = None

        self._gather_facts()

    def _gather_facts(self):
        # Check if easy_install is present
        rc, out, err = utils.execute("easy_install --version")
        if rc == 0:
            self.is_easy_install_present = True
        else:
            self.is_easy_install_present = False
        # Check if pip is present
        rc, out, err = utils.execute("pip --version")
        if rc == 0:
            self.is_pip_present = True
        else:
            self.is_pip_present = False
        # Check if Ansible is present
        rc, out, err = utils.execute("ansible --version")
        if rc == 0:
            self.is_pip_present = True
        else:
            self.is_pip_present = False

    def check_compatibility(self):
        return True

    def is_app_installed(self, app_name):
        result = True
        rc, stdout, stderr = utils.execute("rpm -qa | grep " + app_name)
        if stdout == "" and stderr == "" and rc == 1:
            # app_name is not installed as rpm package
            result = False
        return result

    def is_proc_running(self, proc_name):
        result = True
        rc, stdout, stderr = utils.execute("ps faux | grep -v grep | grep " + proc_name)
        if stdout == "" and stderr == "" and rc == 1:
            # proc_name not found
            result = False
        return result

    def is_port_free(self, port_number):
        result = True
        try:
            sock = socket.socket(socket.SO_REUSEPORT, socket.SO_REUSEADDR)
            sock.bind(('', port_number))
            sock.listen(5)
            sock.close()
        except:
            result = False
        return result

    def configure(self):
        # 1. Setup environment
        self._setup_environemt()
        # 2. Service discovery
        self._service_discovery()
        # 3. Prompt for details
        self._collect_information()
        # 4. Install monitoring
        self._install_monitoring()
        # 5. Run setup for discovered services
        self._configure_service_monitoring()

    def _setup_environemt(self):
        self._enable_epel()
        self._install_ansible()

    def _service_discovery(self):
        utils.out("Running service discovery...")
        # TODO: Implement
        utils.out_ok()

    def _collect_information(self):
        # TODO: Implement
        pass

    def _install_monitoring(self):
        # TODO: Implement
        pass

    def _configure_service_monitoring(self):
        # TODO: Implement
        utils.out("Service configuration...")
        utils.out_ok()

    def _install_ansible(self):
        if not self.is_ansible_present:
            utils.out("Installing Ansible...")
            if not self.config.get("ansible_installed") == "yes":
                if not self.is_pip_present:
                    utils.execute("yum install -y python-pip")
                utils.execute("pip install --upgrade pip")
                utils.execute("pip install --upgrade setuptools")
                utils.execute("yum install -y gcc libffi-devel python-devel openssl-devel")
                rc, out, err = utils.execute("pip install ansible==\'2.1.0\'")
                if rc == 0:
                    self.config.set("ansible_installed", "yes")
                else:
                    utils.out_not_ok()
                    utils.err("Failed to install Ansible")
                    exit(1)
            utils.out_ok()

    def _enable_epel(self):
        utils.out("Enabling EPEL repository...")
        if not self.config.get("epel_enabled") == "yes":
            rc, out, err = utils.execute("yum install epel-release -y")
            if rc == 0:
                self.config.set("epel_enabled", "yes")
            else:
                utils.out_not_ok()
                utils.err("Failed to enable EPEL repository")
                exit(1)
        utils.out_ok()
