FROM python:3.10

WORKDIR ./home

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD bash -c "gunicorn core.wsgi:application --bind 0.0.0.0:8000"