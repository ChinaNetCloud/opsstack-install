#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib import system
from lib.utils import args
from lib import log
from lib import config
from lib import utils
import locale
import os


# TODO: Instead of failing on finding Zabbix installed, verify if it is installed by us, if not exit, else reconfigure


def main():
    choose_language()
    exit(1)
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
    system.load().before_configure()
    system.load().configure()
    log.get_logger().log("Finished installation process")


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
