#bin/bash

# 아래 명령어로 대체.
# docker compose down; docker compose build; docker compose up;

docker rm -f ipfs postgres fastapi_app gradio_app nginx;
docker build ./api -t=fastapi_img:latest;
docker build ./app -t=gradio_img:latest;
docker build ./nginx -t=nginx_img:latest;

docker run \
    -d \
    --name postgres \
    --network=podman \
    --ip=10.88.0.3 \
    -p 5432:5432 \
    --env-file .env \
    postgres:16.2-bookworm;
docker run \
    -d \
    --name fastapi_app \
    # --network=podman \
    # --ip=10.88.0.4 \
    -p 8000:8000 \
    --env-file .env \
    # --add-host=postgres_addr:10.88.0.3 \
    fastapi_img:latest;
docker run \
    -d \
    --name gradio_app \
    # --network=podman \
    # --ip=10.88.0.5 \
    -p 7860:7860 \
    --env-file .env \
    # --add-host=postgres_addr:10.88.0.3 \
    # --add-host=fastapi_addr:10.88.0.4 \
    gradio_img:latest;
docker run \
    -d \
    --name nginx \
    # --network=podman \
    # --ip=10.88.0.6 \
    -p 8080:80 \
    --env-file .env \
    # --add-host=postgres_addr:10.88.0.3 \
    # --add-host=fastapi_app:10.88.0.4 \
    # --add-host=gradio_app:10.88.0.5 \
    nginx_img:latest;
