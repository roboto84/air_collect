=================
air_collect
=================

A simple weather data collector using the Tomorrow.io Weather API.

.. image:: images/ScreenshotAirCollect.png
    :scale: 50

Installation
------------
This project is managed with Python Poetry (https://github.com/python-poetry/poetry). With Poetry installed correctly,
simply clone this project and run::

    poetry install

To test the project, run::

    poetry run pytest

In order to run the program functions, see below.

Introduction
------------
This project functions as part of the larger air project. This particular repository's purpose is
to collect the weather data of a location using the Tomorrow.io Weather API (air_collect.py).

air_collect.py
~~~~~~~~~~~~~~
air_collect.py is named aptly as it is the process in charge of running continuously, polling the Tomorrow.io
Weather API for weather data. It takes the measurements collected from the API requests outputting them out to
the terminal, and aggregating them in the data folder as a collection of CSVs. This process creates a data file
of live weather data readings, along with a data file for a 3 day forecast. air_collect.py requires that
an ``.env`` file is available in the *same* directory it is running under. The format of the .env file
should contain ``CLIMATE_CELL_API_KEY``, ``QUERY_API_INTERVAL``, ``NUM_OF_LIVE_READINGS``, ``COORDINATE_LAT``
and ``COORDINATE_LONG`` as defined environment values.

| ``CLIMATE_CELL_API_KEY`` : The API key of a registered Tomorrow.io Weather API account (https://www.tomorrow.io)
| ``QUERY_API_INTERVAL`` : The amount of seconds to wait before querying the API, i.e. polling interval
| ``NUM_OF_LIVE_READINGS`` : The max number of weather data rows the live data file should hold at any given time. New values continue to be collected indefinitely as long as BarometricMetronome.py is run, but the oldest value is consistently truncated to stay within this predefined limit.
| ``COORDINATE_LONG`` : The location's geographic coordinate system longitude
| ``COORDINATE_LAT`` : The location's geographic coordinate system latitude

An explained ``.env`` file format is shown below::

    CLIMATE_CELL_API_KEY=<your dark sky API key>
    QUERY_API_INTERVAL=<number of seconds between API requests>
    NUM_OF_LIVE_READINGS=<number of readings in the live csv file>
    COORDINATES_LAT=<'lat, long' coordinates>
    COORDINATE_LONG=<'lat, long' coordinates>

A typical ``.env`` file may look like this::

    CLIMATE_CELL_API_KEY=<your dark sky API key>
    QUERY_API_INTERVAL=3600
    NUM_OF_LIVE_READINGS=168
    COORDINATES_LAT=40.71427
    COORDINATE_LONG=-74.00597

To run the script once the environment (.env) file is created, from within the root air_collect directory, simply type::

    poetry run python air_collect/air_collect.py

Logs
-----
Process logs are generated in the project's root directory's log folder.

Commit Conventions
----------------------
Git commit conventions follows Conventional Commits message conventions explained in detail on their website
(https://www.conventionalcommits.org)
