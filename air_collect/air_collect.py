# Air properties collector
import os
import sys
import logging.config
from apscheduler.schedulers.blocking import BlockingScheduler
from air_core.library.air_settings import TIMEZONE
from typing import Any
from dotenv import load_dotenv
from datetime import datetime, timedelta
from air_core.library.air_settings import file_settings, UNITS
from air_core.library.air import Air
from bin.api_payloads import current_readings_payload, five_day_report_payload
from bin.data_source import DataSource
from bin.file_handler import FileHandler
from bin.db.air_db import AirDb


class AirCollect:
    def __init__(self, logging_object: Any, api_key: str, location_lat_long: tuple[float, float],
                 query_interval: int, trim_interval: int, num_of_readings: int, sql_lite_db_path: str):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._live_data_file: str = FileHandler.get_full_file_path(file_settings['live_data']['data_file'])
        self._forecast_data_file: str = FileHandler.get_full_file_path(file_settings['next_days']['data_file'])
        self._air_db: AirDb = AirDb(logging_object, sql_lite_db_path)
        self._api_key: str = api_key
        self._lat_long: tuple[float, float] = location_lat_long
        self._query_api_interval: int = query_interval
        self._trim_date_interval: int = trim_interval
        self._num_of_live_readings: int = num_of_readings

    def _assure_csv_files_state(self, live_data_relative_file_path: str, forecast_relative_file_path: str):
        if not FileHandler.file_exists(live_data_relative_file_path):
            FileHandler.append_line_to_file(self._logger, Air(UNITS).data_key_order(), live_data_relative_file_path)
        if not FileHandler.file_exists(forecast_relative_file_path):
            FileHandler.clear_file(self._logger, forecast_relative_file_path)

    def run_metronome(self) -> None:
        try:
            start_time: str = '2020-10-10 03:00:00'
            self._assure_csv_files_state(self._live_data_file, self._forecast_data_file)
            self._get_current_data()
            self._get_daily_data()
            scheduler: BlockingScheduler = BlockingScheduler(timezone=TIMEZONE)
            scheduler.add_job(self._get_current_data,
                              'interval',
                              start_date=start_time,
                              seconds=self._query_api_interval)
            scheduler.add_job(self._get_daily_data,
                              'cron',
                              day_of_week='*',
                              hour=0,
                              minute='5')
            scheduler.add_job(FileHandler.trim_data,
                              'interval',
                              args=[self._logger, self._live_data_file, self._num_of_live_readings],
                              seconds=self._trim_date_interval)
            scheduler.start()
        except KeyboardInterrupt:
            self._logger.warning('Received a KeyboardInterrupt... exiting process')
            sys.exit()

    def _get_current_data(self) -> None:
        data: dict = DataSource.query_tomorrow_api(self._logger,
                                                   self._api_key,
                                                   self._lat_long,
                                                   current_readings_payload)
        if data:
            air_obj: Air = Air(UNITS, data[0]['values'], data[0]['startTime'])
            self._logger.info(f'{air_obj}')
            self._air_db.insert_current_weather(self._lat_long, air_obj)
            FileHandler.append_line_to_file(self._logger, f'{air_obj.data_to_csv_string()}', self._live_data_file)

    def _get_daily_data(self) -> None:
        start_time: datetime = datetime.now().replace(microsecond=0)
        end_time: datetime = start_time + timedelta(days=4)
        five_day_report_payload['startTime']: str = f'{start_time.isoformat()}Z'
        five_day_report_payload['endTime']: str = f'{end_time.isoformat()}Z'
        data: dict = DataSource.query_tomorrow_api(self._logger,
                                                   self._api_key,
                                                   self._lat_long,
                                                   five_day_report_payload)
        if data:
            self._air_db.clear_location_forecast_weather(self._lat_long)
            FileHandler.clear_file(self._logger, self._forecast_data_file)
            FileHandler.append_line_to_file(self._logger, Air(UNITS).data_key_order(), self._forecast_data_file)
            for day in data:
                air_obj: Air = Air(UNITS, day['values'], day['startTime'])
                self._logger.info(f'{air_obj}')
                self._air_db.insert_forecast_weather(self._lat_long, air_obj)
                FileHandler.append_line_to_file(self._logger, f'{air_obj.data_to_csv_string()}',
                                                self._forecast_data_file)


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('air_collect/bin/logging.conf'), disable_existing_loggers=False)
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        CLIMATE_CELL_API_KEY: str = os.getenv('CLIMATE_CELL_API_KEY')
        QUERY_API_INTERVAL: int = int(os.getenv('QUERY_API_INTERVAL'))
        NUM_OF_LIVE_READINGS: int = int(os.getenv('NUM_OF_LIVE_READINGS'))
        COORDINATE_LAT: float = float(os.getenv('COORDINATE_LAT'))
        COORDINATE_LONG: float = float(os.getenv('COORDINATE_LONG'))
        SQL_LITE_DB: str = os.getenv('SQL_LITE_DB')
        TRIM_DATA_INTERVAL: int = int(QUERY_API_INTERVAL / 3)
        COORDINATES_LAT_LONG: tuple[float, float] = (COORDINATE_LAT, COORDINATE_LONG)

        print(f'\nWeather data collector will run every {QUERY_API_INTERVAL} seconds for '
              f'coordinates {COORDINATES_LAT_LONG}:')
        air_collect: AirCollect = AirCollect(
            logging,
            CLIMATE_CELL_API_KEY,
            COORDINATES_LAT_LONG,
            QUERY_API_INTERVAL,
            TRIM_DATA_INTERVAL,
            NUM_OF_LIVE_READINGS,
            SQL_LITE_DB
        )
        air_collect.run_metronome()
    except TypeError as type_error:
        logger.error(f'Received TypeError: Check that the .env '
                     f'project file is configured correctly: {type_error}')
        exit()
