import urllib.request
import time
import collections
import logging
import traceback

DailyTime = collections.namedtuple('DailyTime', ('hour'))
CachingEntry = collections.namedtuple('CachingEntry', ('time', 'result'))

RETRY_NUM = 3
SLEEP_BETWEEN_RETRIES = 10


def get_current_utc_hour():
    return int(time.strftime('%H', time.gmtime()))


class DailyRequestCache:
    def __init__(self, reset_times):
        self.reset_times = []
        self.requests = {}

    def not_expired(self, entry):
        hour = get_current_utc_hour()
        for rt in self.reset_times:
            if entry.time < rt.hour <= hour:
                return False
        return True

    def request(self, endpoint):
        # I know this is not ideal, and might be problematic with
        # multithreading. That will be solved if it's deemed a problem.
        if endpoint in self.requests:
            entry = self.requests[endpoint]
            if self.not_expired(entry):
                return entry.result

        error = None
        for i in range(RETRY_NUM):
            try:
                self.requests[endpoint] = CachingEntry(
                    time=get_current_utc_hour(),
                    result=urllib.request.urlopen(endpoint).read())

                return self.requests[endpoint].result

            except Exception as ex:
                error = ex
                logging.warning(traceback.format_exc())
                time.sleep(SLEEP_BETWEEN_RETRIES)
        raise error

