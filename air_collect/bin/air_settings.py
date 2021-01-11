#  Configuration for different plotting perspectives

file_settings: dict = {
    'live_data': {
        'data_file': 'data/liveData.csv',
        'diff_file': 'data/differentials/liveDataDiff.csv',
        'diff2_file': 'data/differentials/liveData2ndOrderDiffFile.csv'
    },
    'next_48_hours': {
        'data_file': 'data/next48Data.csv',
        'diff_file': 'data/differentials/next48HrsDataDiffFile.csv'
    },
    'next_7_days': {
        'data_file': 'data/next7DaysData.csv',
        'diff_file': 'data/differentials/next7DaysDataDiffFile.csv'
    }
}
