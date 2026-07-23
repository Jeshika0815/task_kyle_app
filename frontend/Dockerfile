FROM python:3.13-slim

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN cd app && python manage.py collectstatic --noinput

CMD [ "gunicorn", "--chdir", "app", "task_kyle_app.wsgi:application", "--bind", "0.0.0.0:8000" ]
