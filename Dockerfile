FROM python:3.10.5-buster
#FROM pypy:3.9-7.3.9-bullseye

COPY lichess-bot/requirements.txt /m87/requirements.txt

RUN set -xe \
    && cd /m87 \
    && chmod 755 -R /m87 \
    && pip install -r /m87/requirements.txt

COPY lichess-bot /m87/lichess-bot
COPY engine /m87/engine

WORKDIR /m87

CMD ["python", "/m87/lichess-bot/lichess-bot.py", "-v", "--config", "/m87/config.yml"]
