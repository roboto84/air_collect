
INSERT INTO CURRENT_WEATHER (latitude, longitude, date,
                              temp_value, temp_unit,
                              temp_apparent_value, temp_apparent_unit,
                              moon_phase,
                              humidity_value, humidity_unit,
                              dew_point_value, dew_point_unit,
                              weather_code,
                              precipitation_probability_value, precipitation_probability_unit,
                              precipitation_type, pressure_surface_level_value, pressure_surface_level_unit,
                              epa_index_value, epa_index_unit,
                              epa_health_concern, epa_primary_pollutant,
                              particulate_matter10_value, particulate_matter10_unit,
                              particulate_matter25_value, particulate_matter25_unit,
                              pollutant_CO_value, pollutant_CO_unit,
                              pollutant_NO2_value, pollutant_NO2_unit,
                              pollutant_O3_value, pollutant_O3_unit,
                              pollutant_SO2_value, pollutant_SO2_unit,
                              grass_index, tree_index, weed_index)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);