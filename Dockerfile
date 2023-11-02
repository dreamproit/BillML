FROM python:3.11.5-alpine3.18

RUN mkdir -p /usr/src/app/; mkdir -p /usr/src/logs/archives; mkdir -p /bills_data; mkdir -p /datasets_data
WORKDIR /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/"
ENV PATH="/root/.local/bin:$PATH"

RUN apk update; apk add --no-cache \
bash \
curl \
wget \
git \
gcc \
aws-cli \
python3-dev \
musl-dev \
libressl-dev \
libffi-dev \
zeromq-dev \
apache2-utils; \
curl -sSL https://install.python-poetry.org | python3

COPY . /usr/src/app/

RUN poetry lock; poetry install

RUN chmod +x /usr/src/app/entrypoint.sh
