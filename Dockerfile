FROM python:3.11-slim

WORKDIR /Kyle

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /Kyle/app

# Running
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
