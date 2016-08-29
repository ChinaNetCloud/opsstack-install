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
        verify_permissions()
        if args.get_args().conf_file is not None:
            conf = config.load(args.get_args().conf_file)
            if conf.validate() is False:
                utils.err("CONFIG_FILE_INVALID")
                exit(1)
        else:
            utils.err("CONFIG_FILE_INVALID")
            exit(1)
        log.get_logger(config.get("log_dir") + "/install.log", config.get("log_level"))
        log.get_logger().log("Starting installation process")
        utils.confirm("INSTALL_CONFIRM")
        system.load()

        # Collect system information
        utils.out_progress_wait("COLLECT_SYS_INFO")
        try:
            system.load().collect_system_info()
        except Exception as e:
            utils.out_progress_fail()
            raise Exception(e)
        utils.out_progress_done()

        # Perform service discovery
        utils.out_progress_wait("RUN_SERVICE_DISCOVERY")
        try:
            system.load().service_discovery()
        except Exception as e:
            utils.out_progress_fail()
            raise Exception(e)
        utils.out_progress_done()

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
            raise Exception(e)
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
        system.load().install_syslog()
        system.load().install_collector()
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


def verify_permissions():
    utils.out_progress_wait("CHECK_PERMISSIONS")
    if not utils.verify_root_permissions():
        utils.out_progress_fail()
        utils.err("INCORRECT_PERMISSIONS")
        exit(1)
    else:
        utils.out_progress_done()


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


if __name__ == '__main__':
    main()
else:
    print("Should be executed as main script!")
    exit(1)
