#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"

action=${2:-""}

deploy_manager() {
    check_image_result=$($CURRENT_DIR/docker-manager.sh check)

    # if docker image not found or force-build action, build docker image
    if [ "$check_image_result" == "" -o "$action" == "force-build" ]; then
        echo "docker image build..."
        $CURRENT_DIR/docker-manager.sh build
    fi

    $CURRENT_DIR/docker-manager.sh run
}

deploy_miner() {    
    check_image_result=$($CURRENT_DIR/docker-miner.sh check)

    # if docker image not found or force-build action, build docker image
    if [ "$check_image_result" == "" -o "$action" == "force-build" ]; then
        echo "docker image build..."
        $CURRENT_DIR/docker-miner.sh build
    fi

    $CURRENT_DIR/docker-miner.sh run
}

deploy_validator() {
    check_image_result=$($CURRENT_DIR/docker-validator.sh check)

    # if docker image not found or force-build action, build docker image
    if [ "$check_image_result" == "" -o "$action" == "force-build" ]; then
        echo "docker image build..."
        $CURRENT_DIR/docker-validator.sh build
    fi

    $CURRENT_DIR/docker-validator.sh run
}

case $1 in
    manager)
        deploy_manager
        ;;
    miner)
        deploy_miner
        ;;
    validator)
        deploy_validator
        ;;
    *)
        echo "Usage: $0 {manager|miner|validator}"
        exit 1
esac 