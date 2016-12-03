#!/bin/bash

set -e -x -o pipefail

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
IMAGE_NAME=comsoljupyter/integration-test

docker build -t $IMAGE_NAME $BASE_DIR/..

args=(
    --rm
    -p 8000:8000
    -p 65435-65535:65435-65535
    --name comsoljupyter_test
    $IMAGE_NAME 
)

docker run "${args[@]}"
