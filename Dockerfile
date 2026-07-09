FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# app/ is a real Python package (app.main, app.routers, ...), so it must be
# run as "app.main:app" from its parent directory, not flattened into WORKDIR.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
