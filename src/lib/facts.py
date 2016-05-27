from lib import utils

_singleton = None


# Singleton
class _SystemFacts:
    def __init__(self):
        # TODO: Implement facts gathering
        pass

    def check_compatibility(self):
        return True


def collect_facts():
    global _singleton
    if _singleton is None:
        _singleton = _SystemFacts()
        return _singleton
    else:
        return _singleton
    pass


def check_compatibility():
    global _singleton
    return _singleton.check_compatibility()

if __name__ == '__main__':
    exit(1)
