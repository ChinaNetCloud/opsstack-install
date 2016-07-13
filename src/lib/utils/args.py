_args = None


def set_args(args):
    global _args
    if _args is None:
        _args = args


def get_args():
    global _args
    return _args
