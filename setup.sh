#!/bin/bash

# Setup script for local development on VM(We required installation of Oracle Linux or RHEL Series OS)
# If you already have Docker installed, you could not run this script
read -p "Select action(api, front, ver, help and exit)> " action

# Type of action(api -> setup api server, front -> setup front server, ver -> show version, exit -> exit setup)
# please choose your todo on these commands
# note: We require docker

# App position
repos=${HOME}/task_kyle
front_s=${repos}/frontend

app=${HOME}/task_kyle_app
front=${app}/frontend

# show and do install process
insproc() {
    mkdir -p "${HOME}/task_kyle_api"
    items=()
    totals=${#items[@]}
    for i in "${!items[@]}"; do
        printf '[%d/%d] %3d%% %s done' "$i" "$totals" "$((i * 100 / totals))" "${items[$i]}"
        mv "$repos/${items[$i]}" "${HOME}/task_kyle_api/${items[$i]}" || echo "× failed ${items[$i]}" >&2
    done
}

# checking install docker
if ! command -v docker &> /dev/null
then
    echo "Docker is not installed. Could you install it right now?"
    read -p "y/n: " choice
    if [[ $choice == "y" ]]; then
        echo "Installing Docker..."
        sudo dnf -y update
        sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
        sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    elif [[ $choice == "n" ]]; then
        echo "Please install Docker and try again."
        exit 1
    fi

else
    # main logic
    if [[ $action == "api" ]]; then
        insproc "app db_data nginx docker-compose.yml Dockerfile guide.txt"

    elif [[ $action == "front" ]]; then
        insproc "frontend"

    elif [[ $action == "ver" ]]; then
        echo "Task Kyle Version 0.1 Installing script"
        echo "Author. T.Saito2026 TID"
    elif [[ $action == "help" ]]; then
        echo "How to usage: api, front, ver, help, exit"
    elif [[ $action == "exit" ]]; then
        exit 0
    fi
fi
