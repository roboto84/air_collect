# Air properties collector

import requests
import json
import ntpath
import os
import sys
import logging.config
import numpy as np
import pandas as pd
from typing import Any, NoReturn, List
from dotenv import load_dotenv
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from bin.air_settings import file_settings


class AirCollect:

    def __init__(self, logging_object: Any, home_path: str, api_key: str, location_lat_long: str,
                 query_interval: int, trim_interval: int, num_of_readings: int):
        self.home_path: str = home_path
        self.logger: Any = logging_object.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)

        self.live_data_file: str = self.get_full_file_path(file_settings['live_data']['data_file'])
        self.next_48_hours_data_file: str = self.get_full_file_path(file_settings['next_48_hours']['data_file'])
        self.next_7_days_data_file: str = self.get_full_file_path(file_settings['next_7_days']['data_file'])

        self.live_data_diff_file: str = self.get_full_file_path(file_settings['live_data']['diff_file'])
        self.live_data_2nd_order_diff_file: str = self.get_full_file_path(file_settings['live_data']['diff2_file'])
        self.next_48_hours_data_diff_file: str = self.get_full_file_path(file_settings['next_48_hours']['diff_file'])
        self.next_7_days_data_diff_file: str = self.get_full_file_path(file_settings['next_7_days']['diff_file'])

        self.dark_sky_api_url: str = 'https://api.darksky.net/forecast/{}/{}'.format(api_key, location_lat_long)
        self.query_api_interval: int = query_interval
        self.trim_date_interval: int = trim_interval
        self.num_of_live_readings: int = num_of_readings

    def run_metronome(self) -> NoReturn:
        try:
            scheduler: BlockingScheduler = BlockingScheduler()
            scheduler.add_job(self.query_dark_sky_api, 'interval', seconds=self.query_api_interval)
            scheduler.add_job(self.trim_data, 'interval', seconds=self.trim_date_interval)
            scheduler.start()
        except KeyboardInterrupt:
            self.logger.warning('Received a KeyboardInterrupt... exiting process')
            sys.exit()

    @staticmethod
    def standard_time(unix_time: int, time_type: str) -> str:
        if time_type == 'daily':
            return datetime.fromtimestamp(unix_time).strftime('%m/%d')
        elif time_type == 'hourly':
            return datetime.fromtimestamp(unix_time).strftime('%d-%H')
        else:
            return datetime.fromtimestamp(unix_time).strftime('%m/%d %H:%M')

    def get_full_file_path(self, relative_file_path: str) -> str:
        return os.path.join(self.home_path, relative_file_path)

    @staticmethod
    def transform_to_inhg_pressure(mbar_pressure: float) -> float:
        return round(mbar_pressure * 0.029530, 4)

    def delta(self, api_data: List[dict]) -> List[float]:
        pressure_array: List[float] = []
        for tuple_data in api_data:
            pressure_array.append(self.transform_to_inhg_pressure(tuple_data.get('pressure')))
        return np.round(np.diff(pressure_array), 4)

    @staticmethod
    def write_diff(diff_array: List[float], file_name: str):
        with open(file_name, 'w') as diffData:
            diffData.write('Pressure Delta,Time Interval\n')
            for pos, diff in enumerate(diff_array):
                diffData.write('%s,%s\n' % (diff, pos))

    @staticmethod
    def write_live_data(obj_logger: Any, pressure: float, current_time: str, file_name: str):
        obj_logger.info(f'{pressure} inHg')
        with open(file_name, 'a') as liveData:
            liveData.write('%s,%s\n' % (pressure, current_time))

    def write_next_data(self, next_api_data: List[dict], file_name: str, time_type: str):
        with open(file_name, 'w') as nextData:
            nextData.write('Pressure,Time\n')
            for timeInterval in next_api_data:
                nextData.write('%s,%s\n' % (
                    self.transform_to_inhg_pressure(timeInterval.get('pressure')),
                    self.standard_time(timeInterval.get('time'), time_type)))

    def process_live_data_diffs(self) -> NoReturn:
        data: dict = pd.read_csv(self.live_data_file)
        self.write_diff(np.round(np.diff(data['Pressure']), 4), self.live_data_diff_file)
        self.write_diff(np.round(np.diff(data['Pressure'], n=2), 4), self.live_data_2nd_order_diff_file)

    def query_dark_sky_api(self) -> NoReturn:
        response: Any = requests.get(self.dark_sky_api_url)
        if response:
            weather: dict = json.loads(response.text)
            currently: dict = weather.get('currently')
            self.write_live_data(self.logger, self.transform_to_inhg_pressure(currently.get('pressure')),
                                 self.standard_time(currently.get('time'), 'live'), self.live_data_file)
            self.write_next_data(weather.get('hourly').get('data'), self.next_48_hours_data_file, 'hourly')
            self.write_next_data(weather.get('daily').get('data'), self.next_7_days_data_file, 'daily')
            self.write_diff(self.delta(weather.get('hourly').get('data')), self.next_48_hours_data_diff_file)
            self.write_diff(self.delta(weather.get('daily').get('data')), self.next_7_days_data_diff_file)
            self.process_live_data_diffs()
        else:
            self.logger.error(f'API Status code: {response.status_code}')

    def trim_data(self) -> NoReturn:
        # check if data file has reach the configured live data limit
        self.logger.debug('trim data running')
        with open(self.live_data_file, 'r') as data:
            num_lines: int = sum(1 for line in data)

        if num_lines - 1 > self.num_of_live_readings:
            with open(self.live_data_file, 'r') as infile:
                lines: List[str] = infile.readlines()

            with open(self.live_data_file, 'w') as outfile:
                for pos, line in enumerate(lines):
                    if pos != 1:
                        outfile.write(line)

            self.process_live_data_diffs()


if __name__ == '__main__':
    HOME_PATH: str = ntpath.dirname(__file__)
    logging.config.fileConfig(fname=os.path.join(HOME_PATH, 'bin/logging.conf'), disable_existing_loggers=False)
    logger: Any = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        DARK_SKY_API_KEY: str = os.getenv('DARK_SKY_API_KEY')
        QUERY_API_INTERVAL: int = int(os.getenv('QUERY_API_INTERVAL'))
        TRIM_DATA_INTERVAL: int = int(QUERY_API_INTERVAL / 3)
        NUM_OF_LIVE_READINGS: int = int(os.getenv('NUM_OF_LIVE_READINGS'))
        COORDINATES_LAT_LONG: str = os.getenv('COORDINATES_LAT_LONG')

        print('\nBarometric data collector will run every {} seconds for coordinates {}:'.format(QUERY_API_INTERVAL,
                                                                                                 COORDINATES_LAT_LONG))
        air_collect = AirCollect(logging,
                                 HOME_PATH,
                                 DARK_SKY_API_KEY,
                                 COORDINATES_LAT_LONG,
                                 QUERY_API_INTERVAL,
                                 TRIM_DATA_INTERVAL,
                                 NUM_OF_LIVE_READINGS)
        air_collect.run_metronome()
    except TypeError:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
