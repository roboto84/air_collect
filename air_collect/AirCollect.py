# Air properties collector

import requests
import json
import ntpath
import os
import logging.config
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from bin.AirSettings import File_Settings


class AirCollect:
    HOME_PATH = ntpath.dirname(__file__)
    logging.config.fileConfig(fname=os.path.join(HOME_PATH, 'bin/logging.conf'), disable_existing_loggers=False)

    def __init__(self, api_key, location_lat_long, query_interval, trim_interval, num_of_readings):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)

        self.live_data_file = self.get_full_file_path(File_Settings['live_data']['data_file'])
        self.next_48_hours_data_file = self.get_full_file_path(File_Settings['next_48_hours']['data_file'])
        self.next_7_days_data_file = self.get_full_file_path(File_Settings['next_7_days']['data_file'])

        self.live_data_diff_file = self.get_full_file_path(File_Settings['live_data']['diff_file'])
        self.live_data_2nd_order_diff_file = self.get_full_file_path(File_Settings['live_data']['diff2_file'])
        self.next_48_hours_data_diff_file = self.get_full_file_path(File_Settings['next_48_hours']['diff_file'])
        self.next_7_days_data_diff_file = self.get_full_file_path(File_Settings['next_7_days']['diff_file'])

        self.dark_sky_api_url = 'https://api.darksky.net/forecast/{}/{}'.format(api_key, location_lat_long)
        self.query_api_interval = query_interval
        self.trim_date_interval = trim_interval
        self.num_of_live_readings = num_of_readings

    def run_metronome(self):
        try:
            scheduler = BlockingScheduler()
            scheduler.add_job(self.query_dark_sky_api, 'interval', seconds=self.query_api_interval)
            scheduler.add_job(self.trim_data, 'interval', seconds=self.trim_date_interval)
            scheduler.start()
        except KeyboardInterrupt:
            self.logger.warning('Received a KeyboardInterrupt... exiting process')
            exit()

    @staticmethod
    def standard_time(unix_time, time_type):
        if time_type == 'daily':
            return datetime.fromtimestamp(unix_time).strftime('%m/%d')
        elif time_type == 'hourly':
            return datetime.fromtimestamp(unix_time).strftime('%d-%H')
        else:
            return datetime.fromtimestamp(unix_time).strftime('%m/%d %H:%M')

    def get_full_file_path(self, relative_file_path):
        return os.path.join(self.HOME_PATH, relative_file_path)

    @staticmethod
    def transform_to_inhg_pressure(mbar_pressure):
        return round(mbar_pressure * 0.029530, 4)

    def delta(self, api_data):
        pressure_array = []
        for tuple_data in api_data:
            pressure_array.append(self.transform_to_inhg_pressure(tuple_data.get('pressure')))
        return np.round(np.diff(pressure_array), 4)

    @staticmethod
    def write_diff(diff_array, file_name):
        with open(file_name, 'w') as diffData:
            diffData.write('Pressure Delta,Time Interval\n')
            for pos, diff in enumerate(diff_array):
                diffData.write('%s,%s\n' % (diff, pos))

    @staticmethod
    def write_live_data(logger, pressure, current_time, file_name):
        logger.info(f'{pressure} inHg')
        with open(file_name, 'a') as liveData:
            liveData.write('%s,%s\n' % (pressure, current_time))

    def write_next_data(self, next_api_data, file_name, time_type):
        with open(file_name, 'w') as nextData:
            nextData.write('Pressure,Time\n')
            for timeInterval in next_api_data:
                nextData.write('%s,%s\n' % (
                    self.transform_to_inhg_pressure(timeInterval.get('pressure')),
                    self.standard_time(timeInterval.get('time'), time_type)))

    def process_data_feeds(self):
        data = pd.read_csv(self.live_data_file)
        self.write_diff(np.round(np.diff(data['Pressure']), 4), self.live_data_diff_file)
        self.write_diff(np.round(np.diff(data['Pressure'], n=2), 4), self.live_data_2nd_order_diff_file)

    def query_dark_sky_api(self):
        response = requests.get(self.dark_sky_api_url)
        if response:
            weather = json.loads(response.text)
            currently = weather.get('currently')
            self.write_live_data(self.logger, self.transform_to_inhg_pressure(currently.get('pressure')),
                                 self.standard_time(currently.get('time'), 'live'), self.live_data_file)
            self.write_next_data(weather.get('hourly').get('data'), self.next_48_hours_data_file, 'hourly')
            self.write_next_data(weather.get('daily').get('data'), self.next_7_days_data_file, 'daily')
            self.write_diff(self.delta(weather.get('hourly').get('data')), self.next_48_hours_data_diff_file)
            self.write_diff(self.delta(weather.get('daily').get('data')), self.next_7_days_data_diff_file)
            self.process_data_feeds()
        else:
            self.logger.error(f'API Status code: {response.status_code}')

    def trim_data(self):
        # check if data file has reach the configured live data limit
        self.logger.debug('trim data running')
        with open(self.live_data_file, 'r') as data:
            num_lines = sum(1 for line in data)

        if num_lines - 1 > self.num_of_live_readings:
            with open(self.live_data_file, 'r') as infile:
                lines = infile.readlines()

            with open(self.live_data_file, 'w') as outfile:
                for pos, line in enumerate(lines):
                    if pos != 1:
                        outfile.write(line)

            self.process_data_feeds()


if __name__ == '__main__':
    load_dotenv()
    DARK_SKY_API_KEY = os.getenv('DARK_SKY_API_KEY')
    QUERY_API_INTERVAL = int(os.getenv('QUERY_API_INTERVAL'))
    TRIM_DATA_INTERVAL = int(QUERY_API_INTERVAL / 3)
    NUM_OF_LIVE_READINGS = int(os.getenv('NUM_OF_LIVE_READINGS'))
    COORDINATES_LAT_LONG = os.getenv('COORDINATES_LAT_LONG')

    print('\nBarometric data collector will run every {} seconds for coordinates {}:'.format(QUERY_API_INTERVAL,
                                                                                             COORDINATES_LAT_LONG))
    air_collect = AirCollect(DARK_SKY_API_KEY,
                             COORDINATES_LAT_LONG,
                             QUERY_API_INTERVAL,
                             TRIM_DATA_INTERVAL,
                             NUM_OF_LIVE_READINGS)
    air_collect.run_metronome()
