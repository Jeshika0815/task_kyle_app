#!/bin/bash

if [ "$1" = "rm" ]; then
    docker kill discord-bot
    docker rm discord-bot
fi

docker build --no-cache -t discord-bot ./discord_ver
docker run -d --name discord-bot --env-file discord_ver/.env discord-bot
echo "show logs -> docker logs -f discord-bot"
