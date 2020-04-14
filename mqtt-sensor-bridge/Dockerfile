  
FROM python:3.8-alpine

LABEL maintainer="Blue" \
      description="MQTT to InfluxDB Bridge"

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /app
WORKDIR /app

CMD ["python3", "-u", "main.py"]