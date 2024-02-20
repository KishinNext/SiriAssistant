FROM python:3.11-slim-buster as base
LABEL authors="KishinNext"

ENV APP_PATH=/app
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.4.2
ENV PYTHONPATH=$PYTHONPATH:$APP_PATH

WORKDIR $APP_PATH

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        cmake \
        build-essential \
        gcc \
        g++ \
        curl \
        git && \
    apt-get autoremove -y && apt-get clean && \
    rm -rf /usr/local/src/*

RUN pip install "poetry==$POETRY_VERSION"

COPY poetry.lock pyproject.toml $APP_PATH/

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

COPY /src $APP_PATH/

EXPOSE 8080

ENTRYPOINT ["python", "src/main.py"]

FROM base as final