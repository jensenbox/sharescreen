default:
    echo 'Hello, world!'

build:
    docker compose build

up:
    docker compose up --build --menu

down:
    docker compose down --remove-orphans