#!/bin/bash
# 
# conda setup
#
# This is generic to all versions
# for linux 
#
# uses:
#     
# needs:
#
# takes docker config and applies to conda dist
conda env update -n base --file .config/base_environment.yml

