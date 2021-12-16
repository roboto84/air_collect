
import logging.config
import sqlite3
from datetime import datetime
from sqlite3 import Connection, Cursor, Error
from typing import Any


class SqlLiteDb:
    def __init__(self, logging_object: Any, db_location: str):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._db_location: str = db_location

    def _check_table_exists(self, db_cursor: Cursor, table_name: str) -> bool:
        try:
            table_list = db_cursor.execute(
                """SELECT tbl_name FROM sqlite_master WHERE type='table' AND tbl_name=?;""", [table_name]).fetchall()
            if table_list:
                return True
            return False
        except Error as error:
            self._logger.info(f'Error check if tables exist in Air_DB', error)

    @staticmethod
    def _get_time() -> str:
        return datetime.now().strftime('%m/%d/%Y-%H:%M:%S')

    def _db_connect(self) -> Connection:
        try:
            conn: Connection = sqlite3.connect(self._db_location)
            self._logger.debug(f'Opened DB "{self._db_location}" successfully')
            return conn
        except Error as error:
            self._logger.info(f'Air_DB connection failed', error)

    def _db_close(self, live_db_connection: Connection) -> None:
        try:
            live_db_connection.commit()
            live_db_connection.close()
            self._logger.debug(f'Saved and Closed DB "{self._db_location}" successfully')
        except Error as error:
            self._logger.info(f'Air_DB close failed', error)

    def _check_db_state(self, table_names: list[str]) -> bool:
        try:
            conn: Connection = self._db_connect()
            db_cursor: Cursor = conn.cursor()
            db_schema_good: bool = True
            for table_name in table_names:
                db_schema_good = db_schema_good and self._check_table_exists(db_cursor, table_name)
            self._db_close(conn)
            return db_schema_good
        except Error as error:
            self._logger.info(f'Checking Air_DB state failed', error)
