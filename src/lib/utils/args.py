import argparse
import os

_args = None


def get_args():
    global _args
    return _args


def file_validation(value):
    if not type(value) == str:
        raise argparse.ArgumentTypeError("Invalid type %s of file argument" % type(value))
    result = value.strip()
    if os.path.isfile(result):
        result = os.path.abspath(result)
    else:
        raise argparse.ArgumentTypeError("File %s does not exists. Please check documentation" % result)
    try:
        open(result, "r").close()
    except IOError:
        raise argparse.ArgumentTypeError("File %s does not seem to be readable" % result)
    return result


def dir_validation(value):
    if not type(value) == str:
        raise argparse.ArgumentTypeError("Invalid type %s of directory argument" % type(value))
    result = value.strip()
    if os.path.isdir(result):
        result = os.path.abspath(result)
        try:
            open(result + "/1.tmp", "w").close()
            os.unlink(result + "/1.tmp")
        except IOError:
            raise argparse.ArgumentTypeError("Directory %s does not seem to be writable" % result)
    else:
        raise argparse.ArgumentTypeError("Directory %s is invalid or does not exists" % result)
    return result


if _args is None:
    parser = argparse.ArgumentParser(prog="opsstack-configure", description="OpsStack installation tool. It will install required software such as monitoring etc")
    parser.add_argument('--dev', help=argparse.SUPPRESS, required=False, action='store_true', default=False, dest='DEV')
    parser.add_argument('--usa', help=argparse.SUPPRESS, required=False, action='store_true', default=False, dest='USA')
    parser.add_argument('--dry-run', help=argparse.SUPPRESS, required=False, action='store_true', default=False, dest='DRY_RUN')
    parser.add_argument('--config', help="OpsStack configuration file location", required=False, action='store', default="/etc/opsstack/opsstack.conf", type=file_validation, dest='conf_file')
    parser.add_argument('--log-level', help="Logging level", required=False, action='store', default="info", choices=['debug', 'info'], dest='log_level')
    parser.add_argument('-y', '--assume-yes', help="Do not prompt for confirmation, always assume yes", required=False, action='store_true', default=False, dest='assume_yes')
    parser.add_argument('-b', '--batch-install', help="Add batch install tag", required=False, action='store_true', default=False, dest='batch_install')
    _args = parser.parse_args()
