#!/bin/bash

# script for retieving setup from docker
IMAGE=jupyter/datascience-notebook

# get the setup we want to mimic
mkdir -p .info
docker run -it ${IMAGE} bash -c "conda -V" > .info/conda.version
# main cmd here is conda list -e
# the rest if filters to get rid of linux-specific
# and first 3 lines and remove last field restrction

docker run -it ${IMAGE} bash -c "conda list -e -" |tail +4 | grep -v mutex | grep -v linux | grep -v '\-ng' | awk -F= 'BEGIN{print "name: base\nchannels:\n  - conda-forge\n  - defaults\n  - anaconda\ndependencies:"} (NF>0){print "  - "$1}' > .info/datascience-notebook.yml

docker run -it ${IMAGE} bash -c "conda list -e -"  |tail +4 | awk -F= 'BEGIN{print "name: base\nchannels:\n  - conda-forge\n  - defaults\n  - anaconda\ndependencies:"} (NF>0){print "  - "$1}' > .info/datascience-notebook.Linux.yml
