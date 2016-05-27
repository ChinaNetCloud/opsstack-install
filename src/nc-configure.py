#!/usr/bin/python

import os

from lib import facts
from lib import config
from lib import api
from lib import utils


def verify_permissions():
    utils.out("Checking permissions...")
    if not os.geteuid() == 0:
        utils.out_not_ok()
        # TODO: i18n
        utils.err("Not sufficient permissions, please run with sudo. Exiting...")
        exit(1)
    else:
        utils.out_ok()


def collect_facts():
    # TODO: i18n
    utils.out("Collecting system information...")
    facts.collect_facts()
    utils.out_ok()


def check_compatibility():
    # TODO: i18n
    utils.out("Checking system compatibility...")
    if facts.check_compatibility():
        utils.out_ok()
    else:
        utils.out_not_ok()
        # TODO: i18n
        # TODO: Insert link to system requirements web page into message
        utils.err("Current system is not compatible. Please check documentation. Exiting...")
        exit(1)


def verify_api_token():
    while True:
        # TODO: i18n
        utils.out("Connecting to OpsStack...")
        token = config.get_config().get("api_token")
        if token is not None:
            pass
        else:
            utils.out_not_ok()
            # TODO: Sanity check!
            # TODO: i18n
            token = raw_input("  Please enter OpsStack API token:")
            if len(token) > 0:
                config.get_config().set("api_token", token)
            continue
        a = api.Api()
        if a.verify_token():
            utils.out_ok()
            break
        else:
            utils.out_not_ok()
            # TODO: i18n
            utils.err("Invalid API token")


def main():
    # 0. Check if running as root, else exit
    verify_permissions()

    # 1. Collect system information
    collect_facts()

    # 1.1 Check compatibility, exit if not compatible
    check_compatibility()

    # 2. Get and verify API token
    verify_api_token()
    pass

if __name__ == '__main__':
    main()
else:
    print "Should be executed as main script!"
    exit(1)
