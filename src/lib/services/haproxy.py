import abstract
import os

from lib import utils

class Haproxy(abstract.Abstract):
    def __init__(self):
        abstract.Abstract.__init__(self)

    @staticmethod
    def getname():
        return 'haproxy'

    @staticmethod
    def discover(system):
        result = False
        if system.OS == 'linux':
            if system.is_proc_running("haproxy") or system.is_app_installed("haproxy"):
                result = True
        return result

    @staticmethod
    def configure(system):
        utils.out_progress_wait("Configuring nc-haproxy...")
        if not system.config.get("haproxy_configured") == "yes":
            #TODO Modify haproxy.cfg to enable socat and haproxy status page?
            rc, out, err = utils.ansible_play("rhel_haproxy_configure")
            if rc == 0:
                system.config.set("haproxy_configured", "yes")
                utils.out_progress_done()
            else:
                utils.out_progress_fail()
                utils.err("Failed to configure nc-haproxy")
                exit(1)
        else:
            utils.out_progress_skip()
