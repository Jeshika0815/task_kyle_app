# Task Kyle

**Ver Show1**

Task Kyle is text based schedule management service.
This project one of the school group activities.
We will able to connect google oauth, calender and Discord chatbot.
(Now this service is in the prototype stage and support in Japanese only)

[Owner site](https://jeshika0815.github.io/tom2005_webs/)

---
## How to installing?
### 1. Before that
This project is based on Docker.
If you don't have Docker installed, please install from [here](https://docs.docker.com/get-docker/).

### 2. Installation repository
Please install source code below.

Linux/MacOS
```sh
curl -sSL https://jeshika0815.github.io/tom2005_webs/app_install/task_kyle_app/nsetup.sh | bash
```

Windows
```bat
curl -sSL https://jeshika0815.github.io/tom2005_webs/app_install/task_kyle_app/setup.bat | cmd
```

### 3. How to start this service
Please run the following command to start the service.
```sh
cd task_kyle_app # or ./task_kyle_app/frontend -> for frontend hosting
docker-compose up -d  # Start the service

docker-compose ps  # Check the status of the service

docker-compose down -v  # Stop the service
```
