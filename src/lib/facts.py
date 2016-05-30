import platform

_singleton = None


# Singleton
class _SystemFacts:
    def __init__(self):
        # TODO: Implement facts gathering
        self.os = None
        self.os_name = None
        self.os_version = None
        self._gather_facts()
        pass

    def _gather_facts(self):
        self.os = platform.system()
        if self.os == "Linux":
            self._linux_gather_facts()
        elif self.os == "Windows":
            self._windows_gather_facts()
            pass

    def _linux_gather_facts(self):
        self.os_name = platform.linux_distribution(full_distribution_name=0)[0]
        self.os_version = platform.linux_distribution()[1].split('.')[0]

    def _windows_gather_facts(self):
        # TODO: Implement Windows fact gathering
        pass

    def check_compatibility(self):
        result = False
        if self.os == "Linux":
            result = self._linux_compat_check()
        elif self.os == "Windows":
            result = self._windows_compat_check()
        return result

    def _linux_compat_check(self):
        # TODO: Extend supported distributions and versions
        result = False
        if self.os_name == "centos" or self.os_name == "redhat":
            # CentOS currently support only 6 and 7
            if self.os_version in ['6', '7']:
                result = True
        return result

    def _windows_compat_check(self):
        # TODO: Implement Windows compatibility check
        # TODO: Not implement as Windows is not yet supported
        return False


def collect_facts():
    global _singleton
    if _singleton is None:
        _singleton = _SystemFacts()
        return _singleton
    else:
        return _singleton
    pass


def check_compatibility():
    global _singleton
    return _singleton.check_compatibility()

if __name__ == '__main__':
    exit(1)
