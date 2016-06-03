import os
try:
    from ConfigParser import SafeConfigParser as _confparser
except ImportError:
    # Perhaps running in Python3
    from configparser import ConfigParser as _confparser

_singleton = None

_SECTNAME = 'Config'


# Singleton
class _Configuration:
    def __init__(self, config_file):
        self.config = None
        self.config_file = config_file
        if os.path.isfile(self.config_file):
            self.load()
        else:
            self.create()

        self.set("install_path", os.path.abspath(os.path.dirname(__file__) + "../../"))

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

    def delete(self, key):
        self.config.remove_option(_SECTNAME, key)
        self.save()


def load(config_file=None):
    global _singleton
    if _singleton is None:
        if config_file is not None:
            _singleton = _Configuration(config_file)
        else:
            raise Exception("Bad call")
    return _singleton


if __name__ == '__main__':
    exit(1)
