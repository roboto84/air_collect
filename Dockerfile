# syntax=docker/dockerfile:1
FROM python:3.10-slim
WORKDIR /usr/src/air_collect

# Update apt-get
RUN apt-get update -y

# Install poetry
ENV POETRY_VERSION=1.2.0
RUN apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | POETRY_VERSION=${POETRY_VERSION} python3 -
ENV PATH="/root/.local/bin:$PATH"

# Install project dependencies via poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && \
    poetry install

# Set environmental variables for application
ENV QUERY_API_INTERVAL=3600 \
    NUM_OF_LIVE_READINGS=100 \
    COORDINATE_LAT=29.654311 \
    COORDINATE_LONG=-82.395474

# Copy application
COPY . .

# Run application
CMD ["poetry", "run", "python", "air_collect/air_collect.py"]
