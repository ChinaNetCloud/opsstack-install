#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib import system
from lib.utils import args
from lib import log
from lib import config
from lib import utils
import locale
import os
import sys


# TODO: Instead of failing on finding Zabbix installed, verify if it is installed by us, if not exit, else reconfigure


def main():
    try:
        choose_language()

        # Check if running as root
        utils.out_progress_wait("CHECK_PERMISSIONS")
        if not utils.verify_root_permissions():
            utils.out_progress_fail()
            utils.err("INCORRECT_PERMISSIONS_ERR")
            exit(1)
        else:
            utils.out_progress_done()

        # Check config file
        utils.out_progress_wait("CHECK_CONFIG_FILE")
        if args.get_args().conf_file is not None:
            conf = config.load(args.get_args().conf_file)
            if conf.validate() is False:
                utils.out_progress_fail()
                utils.err("CONFIG_FILE_INVALID")
                exit(1)
        else:
            utils.out_progress_fail()
            utils.err("CONFIG_FILE_INVALID")
            exit(1)
        utils.out_progress_done()
        log.get_logger(config.get("log_dir") + "/install.log", config.get("log_level"))
        log.get_logger().log("Starting installation process")

        # Load system class
        system.load()

        # Check system compatibility
        utils.out_progress_wait("CHECK_SYS_COMPATIBILITY")
        if check_compatibility():
            utils.out_progress_done()
        else:
            utils.out_progress_fail()
            utils.err("NOT_COMPATIBLE_ERR")
            log.get_logger().log("System is not compatible for installation process")
            exit(1)

        # Collect system information
        utils.out_progress_wait("COLLECT_SYS_INFO")
        try:
            system.load().collect_system_info()
        except Exception as e:
            utils.out_progress_fail()
            raise e
        utils.out_progress_done()

        # Perform service discovery
        utils.out_progress_wait("RUN_SERVICE_DISCOVERY")
        try:
            system.load().service_discovery()
        except Exception as e:
            utils.out_progress_fail()
            raise e
        utils.out_progress_done()

        if utils.confirm("INSTALL_CONFIRM"):
            log.get_logger().log("User confirmed installation")
        else:
            log.get_logger().log("User rejected installation")
            exit(0)

        # FIXME: Verify API token here

        system.load().get_info()

        # FIXME: Update OpsStack with system info here

        # Install base monitoring
        utils.out_progress_wait("INSTALL_BASIC_MON")
        try:
            system.load().install_base_monitoring()
        except Exception as e:
            utils.out_progress_fail()
            utils.err("FAILED_INSTALL_BASIC_MON")
            raise e
        utils.out_progress_done()

        # Configure services monitoring
        utils.out_progress_wait("RUN_MONITOR_CONFIG")
        try:
            system.load().install_services_monitoring()
        except Exception as e:
            utils.out_progress_fail()
            raise Exception(e)
        utils.out_progress_done()

        # FIXME: Enable monitoring API call

        # Configure syslog
        utils.out_progress_wait("RUN_SYSLOG_CONFIGURATION")
        try:
            system.load().install_syslog()
        except Exception as e:
            utils.out_progress_fail()
            raise Exception(e)
        utils.out_progress_done()

        # Install nc-collector
        utils.out_progress_wait("INSTALL_NC_COLLECTOR")
        try:
            system.load().install_collector()
        except Exception as e:
            utils.out_progress_fail()
            raise Exception(e)
        utils.out_progress_done()

        utils.out("FINISHED_INSTALLATION")

        log.get_logger().log("Finished installation process")
    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        log.get_logger().log("Exception %s, in %s at %s" % (e.message, filename, lineno))
        utils.err("GENERIC_ERROR_MSG")
        exit(1)


def choose_language():
    lang_dict = {
        "1": {"name": "English", "value": "en_US.UTF-8"},
        "2": {"name": "中文", "value": "zh_CN.UTF-8"}
    }
    for i in lang_dict:
        utils.out(i + ". " + lang_dict[i]["name"])
    lang_num = utils.prompt("CHOOSE_LANG")
    if lang_num in lang_dict.keys():
        lang_str = lang_dict[lang_num]["value"]
        os.environ['LANG'] = lang_str
    else:
        utils.out("LANG_USE_DEFAULT")
    locale.setlocale(locale.LC_ALL, "")


def check_compatibility():
    result = True
    if not utils.ansible_lock_exists("zabbix"):
        if system.System.is_app_installed("\"zabbix-agent\""):
            result = False
            log.get_logger().log("Zabbix already installed. Not by us. Aborting.")
        if system.System.is_proc_running("zabbix_agentd"):
            result = False
            log.get_logger().log("Zabbix agent is already running and is not installed by us. Aborting.")
        if not system.System.is_port_free(10050):
            result = False
            log.get_logger().log("Zabbix port is already taken. And it is not us. Aborting.")
    return result


if __name__ == '__main__':
    main()
else:
    print("Should be executed as main script!")
    exit(1)
