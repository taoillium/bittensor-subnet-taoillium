#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd $CURRENT_DIR
parent_dir=$(basename "$(dirname "$(pwd)")")
source $CURRENT_DIR/version.sh

cd ../

SERVICE_TYPE="validator"
VALIDATOR_NAME=${parent_dir}

if [ ! -f "./.env" ]; then
    echo "please create .env file"
    exit 1
fi


# if .env file exists VALIDATOR_NAME, update it
if grep -q "VALIDATOR_NAME=" ./.env; then
    # Cross-platform sed command that works on both macOS and Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/VALIDATOR_NAME=.*/VALIDATOR_NAME=$VALIDATOR_NAME/" ./.env
    else
        # Linux
        sed -i "s/VALIDATOR_NAME=.*/VALIDATOR_NAME=$VALIDATOR_NAME/" ./.env
    fi
else
    # if not exists, add to file end
    echo "" >> ./.env
    echo "VALIDATOR_NAME=$VALIDATOR_NAME" >> ./.env
fi

# if .env file exists VALIDATOR_PORT, update it
if grep -q "VALIDATOR_PORT=" ./.env; then
    # keep existing value
    echo "VALIDATOR_PORT already exists in .env"
else
    # if not exists, add to file end
    echo "" >> ./.env
    echo "VALIDATOR_PORT=8092" >> ./.env
fi

source ./.env

docker_image="bst-validator:${VERSION:-latest}"

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

    docker-compose --env-file .env -f docker/docker-compose.validator.yml build --force-rm
}

run_container() {
    # ensure logs directory exists
    mkdir -p logs
    
    docker-compose --env-file .env -f docker/docker-compose.validator.yml down
    # docker-compose -f docker-compose.validator.yml build
    docker-compose --env-file .env -f docker/docker-compose.validator.yml up -d
}

case $1 in
    build)
        build_image
        ;;
    run)
        run_container
        ;;  
    stop)
        docker-compose --env-file .env -f docker/docker-compose.validator.yml stop
        ;;
    start)
        docker-compose --env-file .env -f docker/docker-compose.validator.yml start
        ;;
    down)
        docker-compose --env-file .env -f docker/docker-compose.validator.yml down
        ;;
    restart)
        docker-compose --env-file .env -f docker/docker-compose.validator.yml restart
        ;;
    check)
        check_image
        ;;
    logs)
        docker-compose --env-file .env -f docker/docker-compose.validator.yml logs -f -n 1000
        ;;
    *)
        echo "Usage: $0 {build|run|stop|start|down|restart|check|logs}"
        exit 1
esac 