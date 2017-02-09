import json
from urllib2 import urlopen
from urllib2 import Request
from urllib2 import HTTPError

from lib import config
from lib import log
from lib.utils import args


_singleton = None


# Singleton
class _Api:
    def __init__(self, url):
        self.token = None
        if url is not None:
            self.api_url = url + "/api/v1%s?apikey=%s"
        elif config.get("opsstack_api_url") is not None:
            self.api_url = config.get("opsstack_api_url") + "/api/v1%s?apikey=%s"
        else:
            if args.get_args().DEV is True:
                self.api_url = "https://opsstack-dev.service.chinanetcloud.com/api/v1%s?apikey=%s"
            else:
                self.api_url = "https://opsstack.chinanetcloud.com/api/v1%s?apikey=%s"
        pass

    def verify_token(self):
        if args.get_args().DRY_RUN:
            return True
        result = False
        # Make sure we have self.token set
        if self.token is None:
            token = config.get("opsstack_api_token")
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

    def update_configuration(self, data):
        if args.get_args().DRY_RUN:
            return True
        result = False
        method = "/hosts/%s/" % config.get('opsstack_host_id')
        success, response = self._api_call(method, post_data=data)
        if success:
            result = True
        return result

    def confirm_configuration(self):
        if args.get_args().DRY_RUN:
            return True
        result = False
        method = "/hosts/%s/actions/monitoring.enable" % config.get('opsstack_host_id')
        success, response = self._api_call(method, {})
        if success:
            result = True
        return result

    def _api_call(self, method, post_data=None):
        result = (False, None)
        url = self.api_url % (method, self.token)
        header = {"Accept": "application/json"}
        log.get_logger().debug("Executing API call to %s" % url)
        if post_data is not None:
            log.get_logger().debug("Payload is %s" % json.dumps(post_data))
        else:
            log.get_logger().debug("No payload for request. Will use GET instead of POST")
        try:
            if post_data is not None:
                req = Request(url, data=json.dumps(post_data), headers=header)
                response = urlopen(req)
            else:
                req = Request(url, data=None, headers=header)
                response = urlopen(req)
            if response is not None:
                if response.getcode() == 200:
                    rc = True
                else:
                    rc = False
                try:
                    data = json.loads(response.read())
                except (TypeError, ValueError):
                    data = response.read()
                result = (rc, data)
                if not rc:
                    log.get_logger().debug("Request failed with response code %d" % response.getcode())
                    log.get_logger().debug("Response content was %s" % data)
            else:
                result = (False, None)
                log.get_logger().debug("API request failed.")
        except HTTPError, e:
            log.get_logger().debug("API request failed with below error")
            log.get_logger().debug("HTTP Error %s: %s" % (e.code, e.reason))
            log.get_logger().debug("Error Message: %s" % json.loads(e.read())['message'])
        return result


def load(url=None):
    global _singleton
    if _singleton is None:
        _singleton = _Api(url)
    return _singleton


if __name__ == '__main__':
    exit(1)
