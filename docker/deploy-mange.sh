#!/bin/bash
cd "$(dirname "$0")"
echo "pwd: $(pwd)"
action=${1:-""}

check_image_result=$(./docker-manage.sh check)

# if docker image not found or force-build action, build docker image
if [ "$check_image_result" == "" -o "$action" == "force-build" ]; then
    echo "docker image build..."
    ./docker-manage.sh build
fi

./docker-manage.sh run
