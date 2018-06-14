from lib import log
from lib import utils
from lib.utils import args
from lib import services
from lib import config
import platform
import socket

_singleton = None

class System:
    def __init__(self):
        # Basic
        self.os = None
        self.distribution = None
        self.version = None

        # Secondary
        self.local_hostname = None
        self.local_domain = None
        self.local_fqdn = None
        self.interfaces = []

        # Found services
        self.services = []

        self.__propagate__()

    def __propagate__(self):
        os = platform.system()
        if os == "Linux":
            self.os = "linux"
            info = platform.linux_distribution(full_distribution_name=0, supported_dists=['amzn', 'centos', 'system', 'debian', 'redhat'])
            distribution = info[0]
            version = info[1]
            log.get_logger().log("Detected OS: %s, distribution: %s, version: %s" % (os, distribution, version))
            # Support centos version 6 and 7
            if distribution == "centos" and (version.startswith("6.") or version.startswith("7.")):
                self.distribution = distribution
                self.version = version
            # Support redhat version 6 and 7
            elif distribution == "redhat" and (version.startswith("6.") or version.startswith("7.")):
                self.distribution = distribution
                self.version = version
            # Amazon Linux 2015 and 2016 is based off the centos 6
            elif distribution == "system" and (version.startswith("2016.") or version.startswith("2015.") or version.startswith("2017.") or version.startswith("2018.")):
                self.distribution = "amazon"
                self.version = version
            # Support Ubuntu 12.04, 14.04 and 16.04
            elif distribution == "Ubuntu" and (version.startswith("12.") or version.startswith("14.") or version.startswith("16.") or version.startswith("18.")):
                self.distribution = "ubuntu"
                self.version = version
            # Support Debian version 7 and 8
            elif distribution == "debian" and (version.startswith("7.") or version.startswith("8.") or version.startswith("9.")):
                self.distribution = distribution
                self.version = version
            # FIXME: Add other supported system below as elif statement
            else:
                log.get_logger().log("Detected OS: %s, distribution: %s, version: %s" % (os, distribution, version))
                raise Exception("Unsupported Linux distribution")
        # Right now only support linux and nothing else
        else:
            raise Exception("Unsupported OS")

    def collect_system_info(self):
        # Get local hostname
        self.local_fqdn = socket.getfqdn()
        self.local_hostname = socket.getfqdn().split(".")[0]
        if len(socket.getfqdn().split(".")) > 1:
            self.local_domain = socket.getfqdn().split(".", 1)[1]
        else:
            self.local_domain = ""

        # Get list of interfaces on the system
        iface_list = utils.get_iface_list()
        for iface in iface_list:
            iface_info = utils.iface_get_info(iface)
            result = {
                'name': iface,
                'type': iface_info['type'],
                'ip4': iface_info['ipv4'],
                'ip6': iface_info['ipv6'],
                'mac': iface_info['mac']
            }
            if result['ip4'] != '' and result['mac'] != '':
                self.interfaces.append(result)

    def service_discovery(self):
        for service in services.servicelist:
            if services.servicelist[service].discover(self):
                log.get_logger().log("Found service %s" % services.servicelist[service].getname())
                self.services.append(services.servicelist[service])

    def get_info(self):
        # Changed this to hostname, not FQDN to CMDB reporter matches
        result = {
            "hostname": self.local_hostname,
            "os": [{
                "name": self.os,
                "distribution": self.distribution,
                "version": self.version
            }],
            "interfaces": self.interfaces,
            "services": []
        }
        for service in self.services:
            item = {
                "name": service.getname(),
                "version": "1.0.0",
                "listen": []
            }
            result["services"].append(item)
        return result

    def install_base_monitoring(self):
        zabbix_host_list = config.get('zabbix_host_list')
        if zabbix_host_list is None or zabbix_host_list == "":
            raise Exception("Cannot get Zabbix hosts from config")
        hn = config.get("opsstack_host_name")
        if hn is None or hn == "":
            raise Exception("Cannot get hostname from config")
        extravars = "opsstack_hostname=%s" % hn
        extravars += " zabbix_host_list=%s" % zabbix_host_list
        rc, out, err = utils.ansible_play("base_monitoring", extravars)
        if not rc == 0:
            raise Exception("Installing basic monitoring failed")

    def install_services_monitoring(self):
        for service in self.services:
            if service.getname() == "memcached":
                continue
            if utils.lock_file_exists('service_%s' % service.getname()):
                log.get_logger().log("Service %s has already been configured before. Asking for reconfiguration." % service.getname())
                configure_mon_str = "RECONFIGURE_SERVICE_CONFIRMATION"
            else:
                configure_mon_str = "CONFIGURE_MONITOR_SERVER"
            prompt_string = utils.print_str(configure_mon_str, service.getname())
            if utils.confirm(prompt_string):
                log.get_logger().log("Configuring %s" % service.getname())
                try:
                    service.configure(self)
                    utils.lock_file_create('service_%s' % service.getname())
                except Exception as e:
                    log.get_logger().log("Configuration of %s failed. See below message" % service.getname())
                    log.get_logger().log(e.message)
                    msg = "GENERIC_SERVICE_CONFIG_ERROR"
                    utils.err(utils.print_str(msg, service.getname()))
            else:
                utils.out_progress_wait(utils.print_str("CONFIGURE_MONITOR", service.getname()))
                utils.out_progress_skip()

    def install_syslog(self):
        syslog_target = config.get('syslog_target')
        if syslog_target is None or syslog_target == "":
            raise Exception("Cannot get syslog target from config")
        hn = config.get("opsstack_host_name")
        if hn is None or hn == "":
            raise Exception("Cannot get hostname from config")
        extravars = "opsstack_hostname=%s" % hn
        extravars += " syslog_target=%s" % syslog_target
        rc, out, err = utils.ansible_play("syslog", extravars)
        if not rc == 0:
            raise Exception("Configuring syslog failed")

    def install_collector(self):
        collector_api_url = config.get('collector_api_url')
        if collector_api_url is None or collector_api_url == "":
            raise Exception("Cannot get collector API URL from config")
        hn = config.get("opsstack_host_name")
        if hn is None or hn == "":
            raise Exception("Cannot get hostname from config")
        extravars = "opsstack_hostname=%s" % hn
        extravars += " collector_api_url=%s" % collector_api_url
        rc, out, err = utils.ansible_play("nc-collector", extravars)
        if not rc == 0:
            raise Exception("nc-collector installation failed")

    def run_collector(self):
        rc, out, err = utils.ansible_play("nc-collector-cron")
        if not rc == 0:
            raise Exception("run nc-collector cron failed")

    def install_goaccess(self):
        # Skip GoAccess completely now
        pass

    def install_filebeat(self):
        rc, out, err = utils.ansible_play("install_filebeat")
        if not rc == 0:
            raise Exception("filebeat installation failed")

    @staticmethod
    def is_proc_running(proc_name):
        result = True
        rc, stdout, stderr = utils.execute("ps faux | grep -v grep | egrep " + proc_name)
        if stdout == "" and rc == 1:
            # proc_name not found
            result = False
        return result

    @staticmethod
    def is_app_installed(app_name):
        result = True
        rc, stdout, stderr = utils.ansible_play("is_app_installed", "package_name=%s" % app_name)
        if rc != 0:
            # app_name is not installed
            result = False
        return result

    @staticmethod
    def is_port_free(port_number):
        result = True
        try:
            sock = socket.socket(socket.SO_REUSEADDR)
            sock.bind(('', port_number))
            sock.listen(5)
            sock.close()
        except socket.error:
            result = False
        return result


def load():
    global _singleton
    if _singleton is None:
        log.get_logger().log("Loading system class")
        _singleton = System()
    return _singleton


if __name__ == '__main__':
    exit(1)
