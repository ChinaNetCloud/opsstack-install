# -*- coding: utf-8 -*-
from lib import utils
from lib import api
from lib import services
from lib import log
from abstract import Abstract

import os
import locale
import re
import logging
LOGGER = logging.getLogger()


class Common(Abstract):
    def before_configure(self):
        log.get_logger().log("Choose running language")
        self.choose_language()
        log.get_logger().log("Verifying permissions")
        self.verify_permissions()
        log.get_logger().log("Running init")
        self.init()
        log.get_logger().log("Checking compatibility")
        self.check_compatibility()
        log.get_logger().log("Gathering facts")
        self.collect_facts()
        log.get_logger().log("Running service discovery")
        self.service_discovery()
        log.get_logger().log("Verifying API token")
        self._verify_api_token()

    def configure(self):
        log.get_logger().log("Collecting needed information")
        self._collect_information()
        log.get_logger().log("Registering with OpsStack")
        self._register_server()
        log.get_logger().log("Setting up the environment")
        self._setup_environemt()
        log.get_logger().log("Installing monitoring")
        self._install_monitoring()
        log.get_logger().log("Configuring syslog")
        self.configure_syslog()
        log.get_logger().log("Installing nc_collector")
        self._install_nc_collector()
        log.get_logger().log("Running configuration for each discovered service")
        self.service_configuration()
        log.get_logger().log("Sending confirmation API request")
        self.confirm_configuration()

    def _verify_api_token(self):
        while True:
            token = self.config.get("api_token")
            if token is None:
                log.get_logger().log("No API token found")
                # TODO: Sanity check!
                # TODO: i18n
                token = utils.prompt("INPUT_OPSSTACK_API")
                if len(token) > 0:
                    self.config.set("api_token", token)
                continue
            # TODO: i18n
            utils.out_progress_wait("CONNECT_OPSSTACK")
            if api.load().verify_token():
                log.get_logger().log("API token passed verification")
                utils.out_progress_done()
                break
            else:
                log.get_logger().log("Bad API token entered")
                utils.out_progress_fail()
                # TODO: i18n
                utils.err("Invalid API token")
                self.config.delete("api_token")

    def choose_language(self):
        choose_dict = {
            "1": {"name": "English", "value": "en_US.UTF-8"},
            "2": {"name": "中文", "value": "zh_CN.UTF-8"}
        }
        for i in choose_dict:
            print i + ". " + choose_dict[i]["name"]
        lang_num = utils.prompt("CHOOSE_LANG")
        if lang_num in choose_dict.keys():
            lang_str = choose_dict[lang_num]["value"]
            os.environ['LANG'] = lang_str
        else:
            utils.out("LANG_USE_DEFAULT")
        locale.setlocale(locale.LC_ALL, "")

    def verify_permissions(self):
        utils.out_progress_wait("CHECK_PERMISSIONS")
        if not self._verify_permissions():
            log.get_logger().log("Not running with enough permissions")
            utils.out_progress_fail()
            # TODO: i18n
            utils.err("NOT_CORRECT_PERM")
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
            log.get_logger().log("Cannot connect to outside using HTTP(S)")
            utils.out_progress_fail()
            # TODO: i18n
            utils.err("CANNOT_CONNECT_INTERNET")
            exit(1)
        # Check connectivity to outside on zbx trapper port
        # TODO: Come up with better than hardcoded IP
        if not utils.test_connection('54.222.237.59', 10051):
            log.get_logger().log("Cannot connect to outisde on Zabbix trapper port 10051")
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
                log.get_logger().log("Found service %s" % services.servicelist[service].getname())
                self.services.append(services.servicelist[service])
        utils.out_progress_done()

    def service_configuration(self):
        utils.out("RUN_MONITOR_CONFIG")
        for service in self.services:
            if self.config.get('service_%s' % service.getname()) is not None:
                log.get_logger().log("Service %s has already been configured before. Asking for reconfiguration." % service.getname())
                configure_mon_str = "RECONFIGURE_SERVICE_CONFIRMATION"
            else:
                configure_mon_str = "CONFIGURE_MONITOR_SERVER"
            prompt_string = utils.print_str(configure_mon_str, service.getname())
            if utils.confirm(prompt_string):
                log.get_logger().log("Configuring %s" % service.getname())
                try:
                    service.configure(self)
                    self.config.set('service_%s' % service.getname(), 'yes')
                except Exception as e:
                    log.get_logger().log("Configuration of %s failed. See below message" % service.getname())
                    log.get_logger().log(e.message)
                    msg = "GENERIC_SERVICE_CONFIG_ERROR"
                    utils.err(utils.print_str(msg, service.getname()))

    def configure_syslog(self):
        utils.out_progress_wait("RUN_SYSLOG_CONFIGURATION")
        if self.config.get('syslog_configured') is not None:
            utils.out_progress_skip()
            return
        try:
            self._configure_syslog()
            utils.out_progress_done()
        except Exception as e:
            log.get_logger().log("Configuration of syslog failed. See below message")
            log.get_logger().log(e.message)
            utils.out_progress_fail()

    def confirm_configuration(self):
        utils.out_progress_wait("CONFIRM_API_CALL")
        result = api.load().confirm_configuration()
        if not result:
            log.get_logger().log("Confirmation API call failed.")
            utils.out_progress_fail()
            exit(1)
        else:
            utils.out_progress_done()

    def _collect_information(self):
        # Prompt for a hostname/purpose if not entered before
        if self.config.get('cust_hostname') is None:
            utils.out("PURPOSE_INFO")
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
