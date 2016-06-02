from lib import config

_singleton = None

# Singleton
class _Api:
    def __init__(self):
        self.config = config.load()
        self.token = None
        pass

    def _verify_token(self):
        # TODO: Implement API call
        return True

    def verify_token(self):
        # Make sure we have self.token set
        if self.token is None:
            token = self.config.get("api_token")
            if token is None:
                return False
            else:
                self.token = token
        # Call API to verify token
        return self._verify_token()

    def register_server(self):
        # TODO: Implement
        return True

    def confirm_configuration(self):
        # TODO: Implement
        return True


def load():
    global _singleton
    if _singleton is None:
        _singleton = _Api()
    return _singleton


if __name__ == '__main__':
    exit(1)
