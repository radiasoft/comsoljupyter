#!/bin/bash

set -e -x -o pipefail

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
IMAGE_NAME=comsoljupyter/integration-test
NAME=comsoljupyter_test

docker rm -f $NAME || true

docker build -t $IMAGE_NAME $BASE_DIR/..

args=(
    --rm
    -p 8000:8000
    -p 65435-65535:65435-65535
    --name $NAME
    $IMAGE_NAME 
)

docker run "${args[@]}"
