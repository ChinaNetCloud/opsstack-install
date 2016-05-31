from lib import config


# Singleton
class Api:
    def __init__(self):
        self.config = config.get_config()
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


if __name__ == '__main__':
    exit(1)
