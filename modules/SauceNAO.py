import json
import requests

from .limiter import ShortLimiter, LongLimiter


class SauceNAO:
    def __init__(self, api_key, output_type=2, testmode=0,
                 dbmask=None, dbmaski=None, db=999, numres=6,
                 shortlimit=20, longlimit=300):
        params = dict()
        params['api_key'] = api_key
        params['output_type'] = output_type
        params['testmode'] = testmode
        params['dbmask'] = dbmask
        params['dbmaski'] = dbmaski
        params['db'] = db
        params['numres'] = numres
        self.params = params

        self.limiters = (ShortLimiter(shortlimit), LongLimiter(longlimit))

    def get_sauce(self, url):
        threads = [limiter.acquire() for limiter in self.limiters]

        self.params['url'] = url
        response = requests.get('https://saucenao.com/search.php', params=self.params)

        if self.verify_http_status(response, threads):
            data = self.load_json(response)
            if data is not None and self.verify_header_status(data, threads):
                return json.loads(response.text)

    def verify_http_status(self, response, threads):
        if response.status_code != 200:
            [thread.cancel() for thread in threads]
            raise TypeError
        else:
            return True

    def verify_header_status(self, data, threads):
        header = data['header']
        if header['status'] != 0:
            [thread.cancel() for thread in threads]
            raise TypeError
        else:
            return True

    def load_json(self, result):
        try:
            data = json.loads(result.text)
            return data
        except ValueError:
            raise ValueError
