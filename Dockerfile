FROM python:3.10.6-buster

COPY lichess-bot/requirements.txt /workdir/requirements.txt

RUN set -xe \
    && cd /workdir \
    && chmod 755 -R /workdir \
    && pip install -r /workdir/requirements.txt

COPY lichess-bot /workdir/lichess-bot
COPY src /workdir/src/

WORKDIR /workdir

CMD ["python3", "-O", "/workdir/lichess-bot/lichess-bot.py", "-v", "--config", "/workdir/config/config.yml"]
