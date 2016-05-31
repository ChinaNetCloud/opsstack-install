import platform

import centos6
import centos7

_singleton = None


def collect_facts():
    global _singleton
    if _singleton is None:
        os = platform.system()
        os_name = platform.linux_distribution(full_distribution_name=0)[0]
        os_version = platform.linux_distribution()[1].split('.')[0]
        if os == "Linux":
            if os_name == "centos":
                if os_version == "6":
                    _singleton = centos6.Facts()
                elif os_version == "7":
                    _singleton = centos7.Facts()
        return _singleton
    else:
        return _singleton
    pass


def check_compatibility():
    global _singleton
    return _singleton.check_compatibility()

if __name__ == '__main__':
    exit(1)
