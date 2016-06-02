from lib import utils
from lib import api
from abstract import Abstract

import re


class Common(Abstract):
    def before_configure(self):
        self.verify_permissions()
        self.init()
        self.check_compatibility()
        self.collect_facts()
        self.service_discovery()

    def configure(self):
        self._collect_information()
        self._register_server()
        self._setup_environemt()
        self._install_monitoring()
        self._configure_service_monitoring()

    def verify_api_token(self):
        while True:
            # TODO: i18n
            utils.out_progress_wait("Connecting to OpsStack...")
            token = self.config.get("api_token")
            if token is not None:
                pass
            else:
                utils.out_progress_fail()
                # TODO: Sanity check!
                # TODO: i18n
                token = utils.prompt("Please enter OpsStack API token:")
                if len(token) > 0:
                    self.config.set("api_token", token)
                continue
            if api.load().verify_token():
                utils.out_progress_done()
                break
            else:
                utils.out_progress_fail()
                # TODO: i18n
                utils.err("Invalid API token")

    def verify_permissions(self):
        utils.out_progress_wait("Checking permissions...")
        if not self._verify_permissions():
            utils.out_progress_fail()
            # TODO: i18n
            utils.err("Not sufficient permissions, please run with sudo. Exiting...")
            exit(1)
        else:
            utils.out_progress_done()

    def collect_facts(self):
        # TODO: i18n
        utils.out_progress_wait("Collecting system information...")
        self._collect_facts()
        utils.out_progress_done()

    def check_compatibility(self):
        # TODO: i18n
        utils.out_progress_wait("Checking system compatibility...")
        if self._check_compatibility():
            utils.out_progress_done()
        else:
            utils.out_progress_fail()
            # TODO: i18n
            # TODO: Insert link to system requirements web page into message
            utils.err("Current system is not compatible. Please check documentation. Exiting...")
            exit(1)

    def service_discovery(self):
        utils.out_progress_wait("Running service discovery... (Not implemented)")
        self._service_discovery()
        utils.out_progress_done()

    def _collect_information(self):
        # Prompt for a hostname/purpose if not entered before
        if self.config.get('cust_hostname') is None:
            utils.out("\nPlease enter the server purpose.\n")
            utils.out("The purpose can be simple such as \"web\", \"app\", \"database\"\n")
            utils.out("or complex such as \"web-test\", \"db-master\" etc.\n")
            utils.out("Allowed characters are letters, numbers, underscore and hyphen.\n")
            utils.out("Minimum 3, maximum 20 characters.\n")
            while True:
                name = utils.prompt("Please input the purpose: ")
                if re.match(r'^[A-z0-9-_]{3,20}$', name.strip()) is not None:
                    self.customer_hostname = name.strip()
                    self.config.set("cust_hostname", self.customer_hostname)
                    break
                else:
                    utils.err("Invalid input!")
        else:
            utils.out_progress_info("Server purpose is  '" + self.config.get('cust_hostname') + "'")
        # TODO: Consider more input
        pass
