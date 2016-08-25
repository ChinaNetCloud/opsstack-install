import os
from ConfigParser import SafeConfigParser as _confparser
from lib import utils

_singleton = None

_SECTNAME = 'Config'


# Singleton
class _Configuration:
    def __init__(self, config_file):
        self.config = None
        self.config_file = config_file
        if os.path.isfile(self.config_file):
            self.load()

    def load(self):
        self.config = _confparser()
        self.config.read(self.config_file)

    def get(self, key, section=None):
        result = None
        if section is None:
            section = _SECTNAME
        try:
            result = self.config.get(section, key)
        except:
            pass
        return result

    def validate(self):
        # FIXME: Add validation of token, host_id and log_dir?
        result = True
        # Machine ID must be matching
        machine_id = utils.get_machine_id()
        conf_machine_id = self.get("machine_id")
        if not machine_id == conf_machine_id:
            result = False
        # OpsStack URL must be set and be either production or DEV
        if self.get("opsstack_api_url") not in ["https://opsstack.chinanetcloud.com", "https://opsstack-dev.service.chinanetcloud.com"]:
            result = False
        # OpsStack API token must be set
        if self.get("opsstack_api_token") is None:
            result = False
        # OpsStack Host ID must be set
        if self.get("opsstack_host_id") is None:
            result = False
        # OpsStack Host Name must be set
        if self.get("opsstack_host_name") is None:
            result = False
        # Logs directory must be set
        if self.get("log_dir") is None:
            result = False
        return result


def load(config_file=None):
    global _singleton
    if _singleton is None:
        if config_file is not None:
            _singleton = _Configuration(config_file)
        else:
            raise Exception("Bad call")
    return _singleton


def get(key, section=None):
    global _singleton
    if _singleton is None:
        raise Exception("Configuration is not initialized")
    else:
        return _singleton.get(key, section)


if __name__ == '__main__':
    exit(1)
