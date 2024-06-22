# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN addgroup --gid 1000 --system app && adduser --uid 1000 --system --group app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

RUN apt update
RUN apt upgrade -y
RUN apt install git -y

COPY app.py app.py
COPY templates templates
COPY static static

EXPOSE 5000

RUN chown -R app:app /app

USER app

CMD ["gunicorn", "-w", "1", "--bind", "0.0.0.0:5000",  "app:app", "--error-logfile", "-", "--access-logfile", "-"]
