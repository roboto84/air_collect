# Collection of various data sources used by Air

import requests
import json
from typing import List, Any


class DataSource:
    @staticmethod
    def query_climate_cell_api_timelines(logger: Any, api_key: str, lat_long: List[float], payload: dict) -> dict:
        url = 'https://data.climacell.co/v4/timelines'
        querystring = {'apikey': api_key}
        payload = payload
        payload['location'] = lat_long
        headers = {'Content-Type': 'application/json'}
        response = requests.request('POST', url, json=payload, headers=headers, params=querystring)
        if response:
            package: dict = json.loads(response.text)
            core_measurements: dict = package['data']['timelines'][0]['intervals']
            return core_measurements
        else:
            logger.error(f'API Status code: {response}')
            return {}
