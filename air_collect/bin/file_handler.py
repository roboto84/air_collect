# File write and trim operations

import os
from typing import NoReturn, Any, List


class FileHandler:
    @staticmethod
    def get_full_file_path(relative_file_path: str) -> str:
        return os.path.abspath(f'data/{relative_file_path}')

    @staticmethod
    def write_data_append(data: str, file_name: str) -> NoReturn:
        with open(file_name, 'a') as liveData:
            liveData.write('%s\n' % data)

    @staticmethod
    def trim_data(logger: Any, data_file_path: str, num_to_trim_to: int) -> NoReturn:
        # check if data file has reach the configured live data limit
        logger.debug('trim data running')
        try:
            with open(data_file_path, 'r') as data:
                num_lines: int = sum(1 for line in data)

            if num_lines - 1 > num_to_trim_to:
                with open(data_file_path, 'r') as infile:
                    lines: List[str] = infile.readlines()

                with open(data_file_path, 'w') as outfile:
                    for pos, line in enumerate(lines):
                        if pos != 1:
                            outfile.write(line)
        except FileNotFoundError as file_not_found:
            logger.error(f'trim_data found no file to trim: {file_not_found}')
            exit()
