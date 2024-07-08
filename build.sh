#!/bin/bash

ASSIGNMENT=$(basename `pwd`)
TIMESTAMP=$(date +%F-%H-%M)
TAG=$ASSIGNMENT-$TIMESTAMP
mkdir -p source
cp ../gradescope/run_autograder ../*.py ../requirements.txt ../key source
cp template.rkt spec.json ../config.json source
docker build -t dbp1/cs2500f24:$TAG -f ../gradescope/Dockerfile .
docker push dbp1/cs2500f24:$TAG
rm -rf source
