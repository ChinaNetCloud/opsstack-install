from lib import config
import json
try:
    # Python 2.x
    from urllib2 import urlopen
    from urllib2 import URLError
except ImportError:
    # Python 3.x
    from urllib.request import urlopen
    from urllib import URLError


_singleton = None


# Singleton
class _Api:
    def __init__(self):
        self.config = config.load()
        self.token = None
        self.api_url = "https://opsstack-dev.service.chinanetcloud.com/api/v1"
        pass

    def verify_token(self):
        # Make sure we have self.token set
        if self.token is None:
            token = self.config.get("api_token")
            if token is None:
                return False
            else:
                self.token = token
        # Call API to verify token
        # return self._api_call('/verify')[0]
        return True

    def register_server(self):
        # TODO: Implement
        return True

    def confirm_configuration(self):
        # TODO: Implement
        return True

    def _api_call(self, route, post_data=None):
        result = (None, None)
        rc = False
        url = self.api_url + route + "?apikey=" + self.token
        try:
            if post_data is not None:
                response = urlopen(url, json.dumps(post_data))
            else:
                response = urlopen(url)
            if response is not None:
                if response.getcode() == "200":
                    rc = True
                try:
                    data = json.loads(response.read())
                except (TypeError, ValueError):
                    data = None
                result = (rc, data)
        except URLError:
            result = None
        return result


def load():
    global _singleton
    if _singleton is None:
        _singleton = _Api()
    return _singleton


if __name__ == '__main__':
    exit(1)
