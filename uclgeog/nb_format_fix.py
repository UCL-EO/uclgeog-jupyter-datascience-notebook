#!/usr/bin/env python

from pathlib import Path; 
import json;


def fix():
  '''
  fix some fields in jupyter_notebook_config.json
  by inserting into the json in the file.

  - in particular, set the sub-dir to start to be 'notebooks'
    y['NotebookApp']['notebook_dir']="notebooks";
  - switch on nbextensions, overriding warnings that sometimes disable as a bug
    y['NotebookApp']['nbserver_extensions']['jupyter_nbextensions_configurator']=True
  
  '''
  infile=Path.home().joinpath('.jupyter','jupyter_notebook_config.json')
  try:
    y=json.load(open(infile,'r'))    
    # notebooks in notebooks
    y['NotebookApp']['notebook_dir']="notebooks";
    # switch extensions on
    y['NotebookApp']['nbserver_extensions']['jupyter_nbextensions_configurator']=True
    # dump
    json.dump(y,open(infile,'w')) 
  except:
    pass

def main():
  fix()

if __name__ == "__main__":
    # execute only if run as a script
    main()
