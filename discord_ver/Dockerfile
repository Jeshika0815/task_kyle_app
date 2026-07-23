FROM python:3.11-slim

WORKDIR /Kyle

COPY ./requirements.txt .
RUN pip install -r ./requirements.txt

COPY . ./discord_ver

CMD [ "python3", "-m", "discord_ver.main" ]
