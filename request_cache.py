import urllib.request
import time
import collections
import logging
import traceback

DailyTime = collections.namedtuple('DailyTime', ('hour'))
CachingEntry = collections.namedtuple('CachingEntry', ('hour', 'day', 'result'))

RETRY_NUM = 3
SLEEP_BETWEEN_RETRIES = 10


def get_current_utc_hour():
    return int(time.strftime('%H', time.gmtime()))


def get_current_day():
    return time.strftime('%Y-%m-%d')


class DailyRequestCache:
    def __init__(self, extra_reset_times):
        self.reset_times = []
        self.requests = {}

    def is_expired(self, entry):
        if entry.day != get_current_day():
            return True

        hour = get_current_utc_hour()
        for rt in self.reset_times:
            if entry.hour < rt.hour <= hour:
                return True
        return False

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
                self.requests[endpoint] = CachingEntry(
                    hour=get_current_utc_hour(),
                    day=get_current_day(),
                    result=result)

                return self.requests[endpoint].result

            except Exception as ex:
                error = ex
                logging.warning(traceback.format_exc())
                time.sleep(SLEEP_BETWEEN_RETRIES)
        raise error
