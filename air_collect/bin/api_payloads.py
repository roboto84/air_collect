#  Payloads for Climacell requests
from typing import List
from bin.air_settings import UNITS, TIMEZONE

fields_for_current: List[str] = ['temperature', 'temperatureApparent', 'dewPoint', 'humidity', 'pressureSurfaceLevel',
                                 'precipitationProbability', 'precipitationType', 'weatherCode', 'epaIndex',
                                 'epaPrimaryPollutant', 'epaHealthConcern', 'particulateMatter25',
                                 'particulateMatter10', 'pollutantO3', 'pollutantNO2', 'pollutantCO', 'pollutantSO2',
                                 'treeIndex', 'grassIndex', 'weedIndex']

fields_for_five_day: List[str] = fields_for_current.copy()
fields_for_five_day.append('moonPhase')

current_readings_payload = {
    'fields': fields_for_current,
    'timesteps': ['current'],
    'units': UNITS,
    'location': [],
    'timezone': TIMEZONE
}

five_day_report_payload = {
    'fields': fields_for_five_day,
    'timesteps': ['1d'],
    'units': UNITS,
    'location': [],
    'timezone': TIMEZONE,
    'startTime': '',
    'endTime': ''
}
