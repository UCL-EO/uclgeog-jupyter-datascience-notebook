#!/bin/bash

# conda recipe
conda init bash
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda install python={pyver}
conda info -a
conda env create --force -n {package_name} --file environment.yml
conda activate {package_name}

