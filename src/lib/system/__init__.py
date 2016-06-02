import platform

import abstract
import centos7
# import centos6

_singleton = None


def load():
    global _singleton
    if _singleton is None:
        os = platform.system()
        os_name = platform.linux_distribution(full_distribution_name=0)[0]
        # TODO: Amazon linux need a fix platform.linux_distribution(supported_dists=['system']) = ('Amazon Linux AMI', '2015.09', '')
        os_version = platform.linux_distribution()[1].split('.')[0]
        if os == "Linux":
            if os_name == "centos":
                if os_version == "7":
                    _singleton = centos7.System()
                # elif os_version == "6":
                #     _singleton = centos6.System()
    return _singleton


if __name__ == '__main__':
    exit(1)
