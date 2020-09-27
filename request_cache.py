import collections
import logging
import time
import traceback
import urllib.request

CachingEntry = collections.namedtuple('CachingEntry', ('time', 'result'))

RETRY_NUM = 3
SLEEP_BETWEEN_RETRIES = 10


class SimpleRequestCache:
    def __init__(self, request_timeout):
        self.request_timeout = request_timeout
        self.requests = {}

    def is_expired(self, entry):
        # Is expired is more than `request_timeout` seconds passed
        return (entry.time + self.request_timeout) < time.time()

    def request(self, endpoint):
        # I know this is not ideal, and might be problematic with
        # multithreading. That will be solved if it's deemed a problem.
        if endpoint in self.requests:
            entry = self.requests[endpoint]
            if not self.is_expired(entry):
                return entry.result

        error = None
        for i in range(RETRY_NUM):
            try:
                result = urllib.request.urlopen(endpoint).read()
                self.requests[endpoint] = CachingEntry(time=time.time(),
                                                       result=result)

                return self.requests[endpoint].result

            except Exception as ex:
                error = ex
                logging.warning(traceback.format_exc())
                time.sleep(SLEEP_BETWEEN_RETRIES)
        raise error
