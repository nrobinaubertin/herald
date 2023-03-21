FROM python:3.11.2-buster

WORKDIR /workdir

COPY lichess-bot/requirements.txt /workdir/requirements.txt
RUN pip install -r /workdir/requirements.txt

COPY lichess-bot /workdir/
COPY src /workdir/engines/
RUN chmod 755 -R /workdir

CMD ["python3", "-O", "/workdir/lichess-bot.py", "-v", "--config", "/workdir/config/config.yml"]
