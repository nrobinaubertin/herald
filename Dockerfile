# FROM python:3.10.5-buster
FROM pypy:3.9-7.3.9-bullseye

COPY lichess-bot/requirements.txt /workdir/requirements.txt

RUN set -xe \
    && cd /workdir \
    && chmod 755 -R /workdir \
    && pip install -r /workdir/requirements.txt

COPY lichess-bot /workdir/lichess-bot
COPY engine /workdir/engine
COPY workdir.py /workdir/run.py

WORKDIR /workdir

CMD ["pypy3", "/workdir/lichess-bot/lichess-bot.py", "-v", "--config", "/workdir/config/config.yml"]
