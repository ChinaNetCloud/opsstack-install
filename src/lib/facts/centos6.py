import platform

from abstract import Abstract

from lib import utils


class Facts(Abstract):
    def __init__(self):
        self.os = "linux"
        self.os_name = "centos"
        self.os_version = "6"

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
        pass
