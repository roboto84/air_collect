# Air properties collector
import os
import sys
import logging.config
from apscheduler.schedulers.blocking import BlockingScheduler
from typing import Any, NoReturn, List
from dotenv import load_dotenv
from datetime import datetime, timedelta
from air_core.library.air_settings import file_settings, UNITS
from air_core.library.air import Air
from bin.api_payloads import current_readings_payload, five_day_report_payload
from bin.data_source import DataSource
from bin.file_handler import FileHandler


class AirCollect:
    def __init__(self, logging_object: Any, api_key: str, location_lat_long: List[float],
                 query_interval: int, trim_interval: int, num_of_readings: int) -> NoReturn:
        self.logger: Any = logging_object.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)

        self.live_data_file: str = FileHandler.get_full_file_path(file_settings['live_data']['data_file'])
        self.next_days_data_file: str = FileHandler.get_full_file_path(file_settings['next_days']['data_file'])

        self.api_key = api_key
        self.lat_long = location_lat_long
        self.query_api_interval: int = query_interval
        self.trim_date_interval: int = trim_interval
        self.num_of_live_readings: int = num_of_readings

    def run_metronome(self) -> NoReturn:
        try:
            start_time = '2020-10-10 03:00:00'
            self.get_current_data()
            self.get_daily_data()
            scheduler: BlockingScheduler = BlockingScheduler()
            scheduler.add_job(self.get_current_data, 'interval', start_date=start_time, seconds=self.query_api_interval)
            scheduler.add_job(self.get_daily_data, 'cron', day_of_week='*', hour=0, minute='5')
            scheduler.add_job(FileHandler.trim_data, 'interval',
                              args=[self.logger, self.live_data_file, self.num_of_live_readings],
                              seconds=self.trim_date_interval)
            scheduler.start()
        except KeyboardInterrupt:
            self.logger.warning('Received a KeyboardInterrupt... exiting process')
            sys.exit()

    def get_current_data(self) -> NoReturn:
        data: dict = DataSource.query_climate_cell_api_timelines(self.logger, self.api_key,
                                                                 self.lat_long, current_readings_payload)
        if data:
            air_obj = Air(UNITS, data[0]['values'], data[0]['startTime'])
            self.logger.info(f'{air_obj}')
            FileHandler.write_data_append(f'{air_obj.data_to_csv_string()}', self.live_data_file)

    def get_daily_data(self) -> NoReturn:
        start_time = datetime.now().replace(microsecond=0)
        end_time = start_time + timedelta(days=4)
        five_day_report_payload['startTime'] = f'{start_time.isoformat()}Z'
        five_day_report_payload['endTime'] = f'{end_time.isoformat()}Z'
        data: dict = DataSource.query_climate_cell_api_timelines(self.logger, self.api_key,
                                                                 self.lat_long, five_day_report_payload)
        if data:
            open(self.next_days_data_file, 'w').close()
            FileHandler.write_data_append(Air(UNITS).data_key_order(), self.next_days_data_file)
            for day in data:
                air_obj = Air(UNITS, day['values'], day['startTime'])
                self.logger.info(f'{air_obj}')
                FileHandler.write_data_append(f'{air_obj.data_to_csv_string()}', self.next_days_data_file)


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('air_collect/bin/logging.conf'), disable_existing_loggers=False)
    logger: Any = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        CLIMATE_CELL_API_KEY: str = os.getenv('CLIMATE_CELL_API_KEY')
        QUERY_API_INTERVAL: int = int(os.getenv('QUERY_API_INTERVAL'))
        TRIM_DATA_INTERVAL: int = int(QUERY_API_INTERVAL / 3)
        NUM_OF_LIVE_READINGS: int = int(os.getenv('NUM_OF_LIVE_READINGS'))
        COORDINATE_LAT: float = float(os.getenv('COORDINATE_LAT'))
        COORDINATE_LONG: float = float(os.getenv('COORDINATE_LONG'))
        COORDINATES_LAT_LONG = [COORDINATE_LAT, COORDINATE_LONG]

        print(f'\nBarometric data collector will run every {QUERY_API_INTERVAL} seconds for '
              f'coordinates {COORDINATES_LAT_LONG}:')
        air_collect = AirCollect(logging, CLIMATE_CELL_API_KEY, COORDINATES_LAT_LONG, QUERY_API_INTERVAL,
                                 TRIM_DATA_INTERVAL, NUM_OF_LIVE_READINGS)
        air_collect.run_metronome()
    except TypeError as type_error:
        logger.error(f'Received TypeError: Check that the .env project file is configured correctly: {type_error}')
        exit()
