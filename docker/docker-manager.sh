#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source $CURRENT_DIR/version.sh
SERVICE_TYPE="manager"


cd $CURRENT_DIR/../


if [ ! -f "./.env" ]; then
    echo "please create .env file"
    exit 1
fi


# if .env file exists MANAGER_PORT, update it
if grep -q "MANAGER_PORT=" ./.env; then
    # keep existing value
    echo "MANAGER_PORT already exists in .env"
else
    # if not exists, add to file end
    echo "" >> ./.env
    echo "MANAGER_PORT=8000" >> ./.env
fi

source ./.env

docker_image="bst-manager:${VERSION:-latest}"

check_image() {
    if [ -n "$(docker images -q $docker_image)" ]; then
        echo "Docker image $docker_image exists."
    else
        echo ""
    fi
}

build_image() {
    if docker images -q $docker_image >/dev/null 2>&1; then
        echo "docker image $docker_image, rebuilding..."
        docker rm -f $(docker ps -a -q --filter ancestor=$docker_image) 2>/dev/null # force remove associated containers
        docker rmi $docker_image 
    else
        echo "docker image $docker_image, building..."
    fi

    docker-compose --env-file .env -f docker/docker-compose.manager.yml build --force-rm
}

run_container() {
    # ensure logs directory exists
    mkdir -p logs
    
    docker-compose --env-file .env -f docker/docker-compose.manager.yml down
    # docker-compose -f docker-compose.manager.yml build
    docker-compose --env-file .env -f docker/docker-compose.manager.yml up -d
}

case $1 in
    build)
        build_image
        ;;
    run)
        run_container
        ;;  
    stop)
        docker-compose --env-file .env -f docker/docker-compose.manager.yml stop
        ;;
    start)
        docker-compose --env-file .env -f docker/docker-compose.manager.yml start
        ;;
    down)
        docker-compose --env-file .env -f docker/docker-compose.manager.yml down
        ;;
    restart)
        docker-compose --env-file .env -f docker/docker-compose.manager.yml restart
        ;;
    check)
        check_image
        ;;
    logs)
        docker-compose --env-file .env -f docker/docker-compose.manager.yml logs -f -n 1000
        ;;
    *)
        echo "Usage: $0 {build|run|stop|start|down|restart|check}"
        exit 1
esac 