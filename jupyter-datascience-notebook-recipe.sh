#!/bin/bash

# script for retieving setup from docker
IMAGE=jupyter/datascience-notebook

# get the setup we want to mimic
mkdir -p .info
docker run -it ${IMAGE} bash -c "conda -V" > .info/conda.version
docker run -it ${IMAGE} bash -c "conda list -e -" > .info/datascience-notebook.yml
 
