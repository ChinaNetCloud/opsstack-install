from lib import utils
from lib import api
from lib import services
from abstract import Abstract

import re


class Common(Abstract):
    def before_configure(self):
        self.verify_permissions()
        self.init()
        self.check_compatibility()
        self.collect_facts()
        self.service_discovery()
        self._verify_api_token()

    def configure(self):
        self._collect_information()
        self._register_server()
        self._setup_environemt()
        self._install_monitoring()
        self.service_configuration()
        self.confirm_configuration()

    def _verify_api_token(self):
        while True:
            token = self.config.get("api_token")
            if token is None:
                # TODO: Sanity check!
                # TODO: i18n
                token = utils.prompt("INPUT_OPSSTACK_API")
                if len(token) > 0:
                    self.config.set("api_token", token)
                continue
            # TODO: i18n
            utils.out_progress_wait("CONNECT_OPSSTACK")
            if api.load().verify_token():
                utils.out_progress_done()
                break
            else:
                utils.out_progress_fail()
                # TODO: i18n
                utils.err("Invalid API token")
                self.config.delete("api_token")

    def verify_permissions(self):
        utils.out_progress_wait("CHECK_PREM")
        if not self._verify_permissions():
            utils.out_progress_fail()
            # TODO: i18n
            utils.err("Not sufficient permissions, please run with sudo. Exiting...")
            exit(1)
        else:
            utils.out_progress_done()

    def collect_facts(self):
        # TODO: i18n
        utils.out_progress_wait("COLLECT_SYS_INFO")
        self._collect_facts()
        utils.out_progress_done()

    def check_compatibility(self):
        # TODO: i18n
        utils.out_progress_wait("CHECK_SYS_COMP")
        # Check connectivity to outside on HTTP(S)
        if not utils.test_connection('www.baidu.com', 80) or not utils.test_connection('www.baidu.com', 443):
            utils.out_progress_fail()
            # TODO: i18n
            utils.err("CANNOT_CONNECT_INTERNET")
            exit(1)
        # Check connectivity to outside on zbx trapper port
        # TODO: Come up with better than hardcoded IP
        if not utils.test_connection('54.222.237.59', 10051):
            utils.out_progress_fail()
            # TODO: i18n
            utils.err("CANNOT_CONNECT_ZABBIX")
            exit(1)
        if self._check_compatibility():
            utils.out_progress_done()
        else:
            utils.out_progress_fail()
            # TODO: i18n
            # TODO: Insert link to system requirements web page into message
            utils.err("NOT_COMP_EXIT")
            exit(1)

    def service_discovery(self):
        utils.out_progress_wait("RUN_SERVICE_DISCOVERY")
        for service in services.servicelist:
            if services.servicelist[service].discover(self):
                self.services.append(services.servicelist[service])
        utils.out_progress_done()

    def service_configuration(self):
        utils.out("RUN_MONITOR_CONFIG")
        for service in self.services:
            configure_mon_str = "CONFIGURE_MONITOR_SERVER"
            prompt_string = utils.print_str(configure_mon_str, service.getname())
            if utils.confirm(prompt_string):
                service.configure(self)

    def _collect_information(self):
        # Prompt for a hostname/purpose if not entered before
        if self.config.get('cust_hostname') is None:
            utils.out("\nPlease enter the server purpose.\n")
            utils.out("The purpose can be simple such as \"web\", \"app\", \"database\"\n")
            utils.out("or complex such as \"web-test\", \"db-master\" etc.\n")
            utils.out("Allowed characters are letters, numbers, underscore and hyphen.\n")
            utils.out("Minimum 3, maximum 20 characters.\n")
            while True:
                name = utils.prompt("INPUT_PURPOSE")
                if re.match(r'^[A-z0-9-_]{3,20}$', name.strip()) is not None:
                    self.customer_hostname = name.strip()
                    self.config.set("cust_hostname", self.customer_hostname)
                    break
                else:
                    utils.err("INVALID_INPUT")
        else:
            server_purpose_info = utils.print_str( "SERVER_PURPOSE", self.config.get('cust_hostname'))
            utils.out_progress_info(server_purpose_info)
        # TODO: Consider more input
        pass

    def is_app_installed(self, app_name):
        return self._is_app_installed(app_name)

    def is_proc_running(self, proc_name):
        return self._is_proc_running(proc_name)

    def is_port_free(self, port_number):
        return self._is_port_free(port_number)
