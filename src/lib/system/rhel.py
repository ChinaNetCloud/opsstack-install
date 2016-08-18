import socket
import fcntl
import struct
import os

from common import Common

from lib import utils
from lib import config
from lib import api
from lib import log


class System(Common):
    def __init__(self, name, version):
        log.get_logger().log("Running RHEL init")
        self.config = None

        self.OS = "linux"
        self.OS_NAME = name
        self.OS_VERSION = version
        self.CONFIG_FILE = "/etc/opsstack/opsstack.conf"
        self.LOG_FILE = "/var/log/opsstack/configure.log"

        self.is_ansible_present = None
        self.is_pip_present = None
        self.is_easy_install_present = None

        self.local_hostname = None
        self.local_domain = None
        self.local_fqdn = None
        self.customer_hostname = None
        self.interfaces = [
            {
                'name': 'eth0',
                'type': 'physical',
                'ip4': "",
                'ip6': "",
                'mac': ""
            }
        ]

        self.services = []

    def init(self):
        self.config = config.load(self.CONFIG_FILE)

    def _verify_permissions(self):
        if not os.geteuid() == 0:
            log.get_logger().log("Running as non-root user")
            return False
        else:
            return True

    def _collect_facts(self):
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
        # Get private IP address (eth0)
        # TODO: Improve private IP detection
        try:
            self.interfaces[0]['ip4'] = self._get_ip_address("eth0")
        except IOError:
            pass
        # Get local names
        self.local_fqdn = socket.getfqdn()
        self.local_hostname = socket.getfqdn().split(".")[0]
        if len(socket.getfqdn().split(".")) > 1:
            self.local_domain = socket.getfqdn().split(".", 1)[1]
        else:
            self.local_domain = ""

    @staticmethod
    def _get_ip_address(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])

    def _check_compatibility(self):
        result = True
        if self.config.get("zabbix_installed") not in ["yes", "in_progress"]:
            if self._is_app_installed("'^zabbix[0-9]\{0,2\}-agent'"):
                result = False
                log.get_logger().log("Zabbix already installed. Not by us. Aborting.")
            if self._is_proc_running("zabbix_agentd"):
                result = False
                log.get_logger().log("Zabbix agent is already running and is not installed by us. Aborting.")
            if not self._is_port_free(10050):
                result = False
                log.get_logger().log("Zabbix port is already taken. And it is not us. Aborting.")
        return result

    def _is_app_installed(self, app_name):
        result = True
        rc, stdout, stderr = utils.execute("rpm -qa | grep " + app_name)
        if stdout == "" and stderr == "" and rc == 1:
            # app_name is not installed as rpm package
            result = False
        return result

    def _is_proc_running(self, proc_name):
        result = True
        rc, stdout, stderr = utils.execute("ps faux | grep -v grep | grep " + proc_name)
        if stdout == "" and stderr == "" and rc == 1:
            # proc_name not found
            result = False
        return result

    def _is_port_free(self, port_number):
        result = True
        try:
            sock = socket.socket(socket.SO_REUSEADDR)
            sock.bind(('', port_number))
            sock.listen(5)
            sock.close()
        except socket.error:
            result = False
        return result

    def _setup_environemt(self):
        self._enable_epel()
        self._install_ansible()
        self._enable_cnc_repo()

    def _register_server(self):
        utils.out_progress_wait("REGISTER_SER_OPSSTACK")
        if self.config.get('opsstack_host_id') is not None:
            # TODO: Must connect to the OpsStack to see if server still active and submit new configuration (new services in case of reconfiguration)
            # Already registered, skipping
            utils.out_progress_skip()
        else:
            services = []
            for s in self.services:
                services.append({
                    'name': s.getname(),
                    'version': '',
                    'listen': []
                })
            data = {
                'purpose': self.config.get('cust_hostname'),
                'hostname': self.local_hostname,
                'os':[
                    {
                        'name': self.OS,
                        'distribution': self.OS_NAME,
                        'version': self.OS_VERSION
                    }
                ],
                'interfaces': self.interfaces,
                'services': services
            }
            if api.load().register_server(data):
                utils.out_progress_done()
            else:
                utils.out_progress_fail()
                exit(1)

    def _install_monitoring(self):
        utils.out_progress_wait("INSTALL_BASIC_MON")
        if not self.config.get("zabbix_installed") == "yes":
            self.config.set("zabbix_installed", "in_progress")
            rc, out, err = utils.ansible_play("rhel_base_monitoring")
            if rc == 0:
                self.config.set("zabbix_installed", "yes")
                utils.out_progress_done()
            else:
                utils.out_progress_fail()
                utils.err("FAILED_INSTALL_BASIC_MON")
                exit(1)
        else:
            utils.out_progress_skip()
        pass

    def _configure_syslog(self):
        hostname = self.config.get('opsstack_host_name')
        if hostname is None:
            hostname = "srv-nc-config-test"
        rc, out, err = utils.ansible_play("rhel_syslog", "opsstack_hostname=%s" % hostname)
        if not rc == 0:
            raise Exception(err)

    def _install_ansible(self):
        utils.out_progress_wait("INSTALL_ANSIBLE")
        if not self.config.get("ansible_installed") == "yes" and not self.is_ansible_present:
            self.config.set("ansible_installed", "in_progress")
            if not self.is_pip_present:
                utils.execute("yum install -y python-pip")
            utils.execute("pip install --upgrade pip")
            utils.execute("pip install --upgrade setuptools")
            utils.execute("yum install -y gcc libffi-devel python-devel openssl-devel libselinux-python")
            rc, out, err = utils.execute("pip install ansible==\'2.1.0\'")
            if rc == 0:
                self.config.set("ansible_installed", "yes")
                utils.out_progress_done()
            else:

                utils.out_progress_fail()
                utils.err("FAILED_INSTALL_ANSIBLE")
                exit(1)
        else:
            utils.out_progress_skip()

    def _install_nc_collector(self):
        utils.out_progress_wait("INSTALL_NC_COLLECTOR")
        if not self.config.get("cnc_repo_enabled") == "yes":
            utils.out_progress_fail()
            utils.err("CNC_REPO_NOT_ENABLED")
            exit(1)
        elif self.config.get("cnc_repo_enabled") == "yes" and not self.config.get("nc_collector_installed") == "yes":
            rc, out, err = utils.execute("yum install -y nc-collector.noarch")
            if rc == 0:
                self.config.set("nc_collector_installed", "yes")
                utils.out_progress_done()
            else:
                utils.out_progress_fail()
                utils.err("FAILED_INSTALL_NC_COLLECTOR")
                exit(1)
        else:
            utils.out_progress_skip()
        '''
            Make sure crond has been reloaded after installing nc_collector.
            Currently, it will reload crond with the command "/etc/init.d/crond reload" during installing nc_collector,
            but this will fail in CentOS7, so add following command to make crond is reloaded correctly.
            This can be removed in the future if we fixed this in our rpm package.
        '''
        utils.execute("service crond reload")

    def _enable_cnc_repo(self):
        utils.out_progress_wait("ENABLE_CNC_REPO")
        if not self.config.get("cnc_repo_enabled") == "yes":
            rc, out, err = utils.ansible_play("rhel_cnc_repo")
            if rc == 0:
                self.config.set("cnc_repo_enabled", "yes")
                utils.out_progress_done()
            else:
                utils.out_progress_fail()
                utils.err("FAILED_ENABLE_CNC_REPO")
                exit(1)
        else:
            utils.out_progress_skip()
        # Make sure CNC repo is enabled not only installed
        utils.execute("yum-config-manager --enable cnc")

    def _enable_epel(self):
        utils.out_progress_wait("ENABLE_EPEL")
        if not self.config.get("epel_repo_enabled") == "yes":
            rc, out, err = utils.execute("yum install epel-release yum-utils -y")
            if rc == 0:
                self.config.set("epel_repo_enabled", "yes")
                utils.out_progress_done()
            else:
                utils.out_progress_fail()
                utils.err("Failed to enable EPEL repository")
                exit(1)
        else:
            utils.out_progress_skip()
        # Make sure EPEL repo is enabled not only installed
        utils.execute("yum-config-manager --enable epel")
