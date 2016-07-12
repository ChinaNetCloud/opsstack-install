import json

from lib import config
from lib.utils import args

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
        self.api_url = "https://opsstack-dev.service.chinanetcloud.com/api/v1%s?apikey=%s"
        pass

    def verify_token(self):
        if args.get_args().DRY_RUN:
            return True
        result = False
        # Make sure we have self.token set
        if self.token is None:
            token = self.config.get("api_token")
            if token is None:
                return False
            else:
                self.token = token
        # Call API to verify token
        if self._api_call('/verify')[0] is True:
            result = True
        else:
            self.token = None
        return result

    def register_server(self, data):
        if args.get_args().DRY_RUN:
            return True
        result = False
        success, response = self._api_call('/hosts', post_data=data)
        if success:
            self.config.set('opsstack_host_id', response['data']['id'])
            result = True
        return result

    def confirm_configuration(self):
        if args.get_args().DRY_RUN:
            return True
        result = False
        method = "/hosts/%s/actions/monitoring.enable" % self.config.get('opsstack_host_id')
        success, response = self._api_call(method, json.loads("{\"what\":\"that\"}"))
        if success:
            result = True
        return result

    def _api_call(self, method, post_data=None):
        result = (False, None)
        url = self.api_url % (method, self.token)
        try:
            if post_data is not None:
                response = urlopen(url, json.dumps(post_data))
            else:
                response = urlopen(url)
            if response is not None:
                if response.getcode() == 200:
                    rc = True
                else:
                    rc = False
                try:
                    data = json.loads(response.read())
                except (TypeError, ValueError):
                    data = None
                result = (rc, data)
            else:
                result = (False, None)
        except URLError:
            pass
        return result


def load():
    global _singleton
    if _singleton is None:
        _singleton = _Api()
    return _singleton


if __name__ == '__main__':
    exit(1)
