#!/bin/bash
# 
# sort packages from apt.txt 
#
# This is generic to all versions
# for linux. It could be more robust
# but can be done manually from apy.txt
# rather than trying to 2nd guess the system pkg manager 
#
# uses:
#     env.sh
#     apt.txt
#
# needs:
#     curl
#     bash
#

line="##########################"
SUDO=''

echo $line
export MACH=`uname -s`

# name fix for miniconda files
if [ ${MACH} ==  "Darwin" ]
then MACH="MacOSX"
fi

echo $MACH
echo $line
uname -a
echo $line

#
echo "before_install" 
source env.sh 

# could generalise this and check environment
# but will assume these setting for now
#
# assume apt
if [ ${MACH} == "Linux" ]
then
  pkg=apt-get
  ${SUDO} apt-get update
  suffix='sh'
elif [ ${MACH} == "MacOSX" ]
then
  pkg=brew
  # no SUDO for brew
  SUDO=''
  suffix='sh'
elif [ ${MACH} == "Windows" ]
then
  SUDO=''
  pkg=choco
  suffix='exe'
fi


# command line parse


THIS=`basename $0`
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -p|--package_manager)
    pkg="$2"
    shift # past argument
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
    echo "$THIS [-pkg|--package_manager $pkg]"
    echo "      [-s|--sudo] | [-n|-no_sudo]']"
    shift # past argument
    exit
esac
done
set -- "${POSITIONAL[@]}"

echo "package manager: $pkg"

# try an update call
$pkg update

# install packages
grep -v '#' < apt.txt | xargs ${SUDO} ${pkg} install

echo "pkgs setup done"

