#  Configuration for different plotting perspectives

file_settings: dict = {
    'live_data': {
        'data_file': 'liveData.csv',
        'diff_file': 'differentials/liveDataDiff.csv',
        'diff2_file': 'differentials/liveData2ndOrderDiffFile.csv'
    },
    'next_48_hours': {
        'data_file': 'next48Data.csv',
        'diff_file': 'differentials/next48HrsDataDiffFile.csv'
    },
    'next_7_days': {
        'data_file': 'next7DaysData.csv',
        'diff_file': 'differentials/next7DaysDataDiffFile.csv'
    }
}
