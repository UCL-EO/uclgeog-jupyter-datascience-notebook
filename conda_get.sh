#!/bin/bash
# 
# conda getup
#
# This is generic to all versions
# for linux 
#
# uses:
#     env.sh
#     apt.txt
#     
# needs:
#     curl
#     bash
#
# Installs homebrew and miniconda
#
#
TMP=/tmp
line="##########################"
SUDO=''

TAG='2020.02'
suffix='sh'
echo $line
export MACH=`uname -s`

# name fix for miniconda files
if [ ${MACH} ==  "Darwin" ]
then MACH="MacOSX"
fi

if [ ${MACH} ==  "Windows" ]
then suffix.'exe'
# tmp???
fi

echo $MACH
echo $line
uname -a
echo $line

#
echo "before_install" 
#source env.sh 

REPO=https://repo.anaconda.com/archive/
MINI=Anaconda3-${TAG}-${MACH}-x86_64.${suffix}
ANA='ana'

THIS=`basename $0`
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -a|--anaconda)
    REPO=https://repo.anaconda.com/archive/
    TAG='2020.02'
    MINI=Anaconda3-${TAG}-${MACH}-x86_64.${suffix}
    ANA='ana'
    shift # past value
    ;;
    -m|--miniconda)
    REPO=https://repo.anaconda.com/miniconda
    TAG='latest'
    MINI=Miniconda3-${TAG}-${MACH}-x86_64.${suffix}
    ANA='mini'
    shift # past value
    ;;
    -s|--sudo)
    SUDO=sudo
    shift # past argument
    ;;
    -n|--no_sudo)
    SUDO=''
    shift # past argument
    ;;
    -h|--help)
    echo "$THIS [-m|--miniconda] [-a|-anaconda]"
    echo "      [-s|--sudo] | [-n|-no_sudo]']"
    shift # past argument
    exit
esac
done
set -- "${POSITIONAL[@]}"


#
# download and install
#
echo "** 1/3: downloading ${MINI}: ${REPO}/${MINI}"
curl ${REPO}${MINI} -o ${TMP}/${ANA}conda.sh

echo ${TMP}/${ANA}conda.sh

mkdir -p $HOME/${ANA}conda
echo "** 2/3: installing ${TMP}/${ANA}conda.sh to $HOME/${ANA}conda"
if [$SUDO == '']; then
  CONDA_DIR=$HOME/${ANA}conda
else
  # not sure where ... check
  CONDA_DIR=$HOME/${ANA}conda
fi

/bin/bash ${TMP}/${ANA}conda.sh -bu -p ${CONDA_DIR}
rm -f ${TMP}/${ANA}conda.sh

echo "** 3/3: set env variables"
# source the conda setup
if [[ -z ${CONDA_DIR} ]];
then
    echo "variable CONDA_DIR is not set"
    CONDA_DIR=${HOME}/${ANA}conda
else
    echo "variable named CONDA_DIR is already set"
fi

source ${CONDA_DIR}/etc/profile.d/conda.sh
hash -r

echo "pre-setup done"

