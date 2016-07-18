from lib import log
import platform

import abstract
import rhel

_singleton = None


def load():
    log.get_logger().log("Loading system file")
    global _singleton
    if _singleton is None:
        os = platform.system()
        os_name = platform.linux_distribution(full_distribution_name=0)[0]
        # TODO: Amazon linux need a fix platform.linux_distribution(supported_dists=['system']) = ('Amazon Linux AMI', '2015.09', '')
        os_version = platform.linux_distribution()[1].split('.')[0]
        log.get_logger().log("Detected OS: %s, distribution: %s, version: %s" % (os, os_name, os_version))
        if os == "Linux":
            if os_name == "centos":
                if os_version in ["6", "7"]:
                    _singleton = rhel.System(platform.linux_distribution()[0], platform.linux_distribution()[1])
    return _singleton


if __name__ == '__main__':
    exit(1)
