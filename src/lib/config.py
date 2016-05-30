from os.path import isfile
try:
    from ConfigParser import SafeConfigParser as _confparser
except:
    # Perhaps running in Python3
    from configparser import ConfigParser as _confparser

_singleton = None

_SECTNAME = 'Config'


# Singleton
class _Configuration:
    def __init__(self):
        self.config = None
        self.config_file = "/etc/.nc-config"
        if isfile(self.config_file):
            self.load()
        else:
            self.create()

    def load(self):
        self.config = _confparser()
        self.config.read(self.config_file)

    def create(self):
        self.config = _confparser()
        self.config.read(self.config_file)
        self.config.add_section(_SECTNAME)
        self.save()

    def save(self):
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    def get(self, key):
        result = None
        try:
            result = self.config.get(_SECTNAME, key)
        except:
            pass
        return result

    def set(self, key, value):
        self.config.set(_SECTNAME, key, value)
        self.save()


def get_config():
    global _singleton
    if _singleton is None:
        _singleton = _Configuration()
        return _singleton
    else:
        return _singleton
    pass


if __name__ == '__main__':
    exit(1)
else:
    _singleton = _Configuration()
