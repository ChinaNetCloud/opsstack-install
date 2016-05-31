from urllib2 import urlopen as _dl

import abstract


class CentosSetup(abstract.Abstract):
    def __init__(self, facts):
        abstract.Abstract.__init__(self, facts)

    def configure(self):
        pass

    def install_monitoring(self):
        pass

if __name__ == '__main__':
    exit(1)