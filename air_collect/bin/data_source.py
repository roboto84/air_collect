# Collection of various data sources used by Air

import requests
import json
from typing import Any


class DataSource:
    @staticmethod
    def query_tomorrow_api(logger: Any, api_key: str, lat_long: tuple[float, float], payload: dict) -> dict:
        try:
            url = 'https://data.climacell.co/v4/timelines'
            querystring = {'apikey': api_key}
            payload = payload
            payload['location']: list[float] = [lat_long[0], lat_long[1]]
            headers = {'Content-Type': 'application/json'}
            response = requests.request('POST', url, json=payload, headers=headers, params=querystring)
            if response:
                package: dict = json.loads(response.text)
                core_measurements: dict = package['data']['timelines'][0]['intervals']
                return core_measurements
            else:
                logger.error(f'API Status code: {response}')
                return {}
        except Exception as e:
            logger.exception(f'Exception was thrown', e)
