from lib import facts

from centos import CentosSetup

_singleton = None


def get_setup():
    global _singleton
    if _singleton is None:
        if facts.collect_facts().os == "Linux":
            if facts.collect_facts().os_name == "centos":
                _singleton = CentosSetup()
    return _singleton


if __name__ == '__main__':
    exit(1)

