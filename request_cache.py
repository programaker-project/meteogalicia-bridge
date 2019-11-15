import urllib.request
import time
import collections

DailyTime = collections.namedtuple('DailyTime', ('hour'))
CachingEntry = collections.namedtuple('CachingEntry', ('time', 'result'))


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
        if endpoint in self.requests:
            entry = self.requests[endpoint]
            if self.not_expired(entry):
                return entry.result

        # I know this is not ideal, and might be problematic with
        # multithreading. That will be solved if it's deemed a problem.
        self.requests[endpoint] = CachingEntry(
            time=get_current_utc_hour(),
            result=urllib.request.urlopen(endpoint).read())

        return self.requests[endpoint].result
