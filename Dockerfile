FROM python:3.10-buster

ADD . /app/
WORKDIR /app

RUN pip install --upgrade pip \
&& pip install -r requirements.txt

EXPOSE 80

CMD uvicorn main:app --workers 1 --host 0.0.0.0 --port 80