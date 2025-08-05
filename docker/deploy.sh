#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"

name=$1
action=${2:-""}

deploy() {
    check_image_result=$($CURRENT_DIR/docker-$name.sh check)

    # if docker image not found or build-run action, build docker image
    if [ "$check_image_result" == "" -o "$action" == "build-run" ]; then
        echo "docker image build..."
        $CURRENT_DIR/docker-$name.sh build
    fi

    if [ "$action" == "build-run" ]; then
        action="run"
    fi
    $CURRENT_DIR/docker-$name.sh $action
}

case $1 in
    manager|miner|validator)
        deploy
        ;;
    *)
        echo "Usage: $0 {manager|miner|validator} <build-run|run|stop|start|up|down|restart|check|logs>"
        exit 1
esac 