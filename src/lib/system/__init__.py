from lib import log
from lib import utils
from lib import services
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
            info = platform.linux_distribution(full_distribution_name=0, supported_dists=['amzn', 'centos', 'system', 'debian'])
            distribution = info[0]
            version = info[1]
            log.get_logger().log("Detected OS: %s, distribution: %s, version: %s" % (os, distribution, version))
            # Support centos version 6 and 7
            if distribution == "centos" and (version.startswith("6.") or version.startswith("7.")):
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
            result = {
                'name': iface,
                'type': utils.iface_get_type(iface),
                'ip4': utils.iface_get_ip4_address(iface),
                'ip6': utils.iface_get_ip6_address(iface),
                'mac': utils.iface_get_mac_address(iface)
            }
            self.interfaces.append(result)

    def service_discovery(self):
        for service in services.servicelist:
            if services.servicelist[service].discover(self):
                log.get_logger().log("Found service %s" % services.servicelist[service].getname())
                self.services.append(services.servicelist[service])

    def get_info(self):
        pass

    def install_base_monitoring(self):
        pass

    def install_services_monitoring(self):
        pass

    def install_syslog(self):
        pass

    def install_collector(self):
        pass


def load():
    log.get_logger().log("Loading system file")
    global _singleton
    if _singleton is None:
        _singleton = System()
    return _singleton


if __name__ == '__main__':
    exit(1)
