#!/usr/bin/python

import os

from lib import utils

# TODO: Check if system has already been configured before, yes - verify to reconfigure
# TODO: Find a unique identifier for the server (MAC? IP? Keys? All of the above?)


def verify_permissions():
    utils.out_progress_wait("Checking permissions...")
    if not os.geteuid() == 0:
        utils.out_progress_fail()
        # TODO: i18n
        utils.err("Not sufficient permissions, please run with sudo. Exiting...")
        exit(1)
    else:
        utils.out_progress_done()


def collect_facts():
    # TODO: i18n
    utils.out_progress_wait("Collecting system information...")
    system.load()
    utils.out_progress_done()


def check_compatibility():
    # TODO: i18n
    utils.out_progress_wait("Checking system compatibility...")
    if system.load().check_compatibility():
        utils.out_progress_done()
    else:
        utils.out_progress_fail()
        # TODO: i18n
        # TODO: Insert link to system requirements web page into message
        utils.err("Current system is not compatible. Please check documentation. Exiting...")
        exit(1)


def verify_api_token():
    while True:
        # TODO: i18n
        utils.out_progress_wait("Connecting to OpsStack...")
        token = config.get_config().get("api_token")
        if token is not None:
            pass
        else:
            utils.out_progress_fail()
            # TODO: Sanity check!
            # TODO: i18n
            token = utils.prompt("Please enter OpsStack API token:")
            if len(token) > 0:
                config.get_config().set("api_token", token)
            continue
        if api.load().verify_token():
            utils.out_progress_done()
            break
        else:
            utils.out_progress_fail()
            # TODO: i18n
            utils.err("Invalid API token")


def is_zabbix_installed():
    # TODO: i18n
    utils.out_progress_wait("Checking if Zabbix already installed...")
    if not system.load().is_app_installed("zabbix"):
        utils.out_progress_done()
    else:
        utils.out_progress_fail()
        # TODO: i18n
        utils.err("Zabbix already installed. Aborting....")
        exit(1)


def is_zabbix_running():
    # TODO: i18n
    utils.out_progress_wait("Checking if Zabbix agent is running...")
    if not system.load().is_proc_running("zabbix_agent"):
        utils.out_progress_done()
    else:
        utils.out_progress_fail()
        # TODO: i18n
        utils.err("Zabbix agent already running. Aborting....")
        exit(1)


def system_check():
    # 0. Check if running as root, else exit
    verify_permissions()
    from lib import api
    from lib import config
    from lib import system
    global api
    global config
    global system
    # 1. Collect system information
    collect_facts()
    # 1.1 Check compatibility, exit if not compatible
    check_compatibility()
    # 2. Get and verify API token
    verify_api_token()
    # 3. Check if Zabbix-agent is installed/running
    # TODO: Add more checks?
    is_zabbix_installed()
    is_zabbix_running()


def post_check():
    while True:
        confirmation = utils.prompt("Please type \"Yes\" to continue or \"No\" to cancel: ")
        if confirmation == "Yes":
            return True
        elif confirmation == "No":
            utils.err("User cancelled setup")
            exit(1)
        else:
            continue


def setup():
    system.load().configure()


def main():
    # Check system readiness
    system_check()
    # Confirm user wants to install
    post_check()
    # Setup OpsStack components
    setup()
    pass

if __name__ == '__main__':
    main()
else:
    print("Should be executed as main script!")
    exit(1)
