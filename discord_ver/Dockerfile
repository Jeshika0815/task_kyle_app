FROM python:3.11-slim

WORKDIR /Kyle

COPY . /Kyle/discord-service
RUN pip install -r /Kyle/discord-service/requirements.txt

CMD [ "python", "/Kyle/discord-service/main.py" ]
