FROM jupyter/datascience-notebook
# Docker install
#
#
COPY . ${HOME}

RUN /bin/bash get_pkgs.sh 

# Only use this if you dont have miniconda
#RUN /bin/bash conda_get.sh

RUN python uclgeog/batch.py
#USER uclgeog

ENTRYPOINT ["/bin/bash"]
