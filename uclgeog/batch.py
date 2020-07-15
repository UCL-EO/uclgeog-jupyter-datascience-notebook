#!/usr/bin/env python

'''
shell front end to run a set of batch codes
from python, with variable substitution from 
a metedata file
'''  

__author__ = "P Lewis"
__copyright__ = "Copyright 2020 P Lewis"
__license__ = "GPLv3"
__email__ = "p.lewis@ucl.ac.uk"

# this should be robust to OS
# https://stackoverflow.com/questions/14894993/running-windows-shell-commands-with-python
from subprocess import check_output

import yaml
import json
import os
import sys
import getopt
from pathlib import Path
from pandas.io.json._normalize import nested_to_record

from get_env import getEnv


class Batch():
  '''
  run batch recipe from python
  with variable substitution from meta

  '''
  def __init__(self,scripts=['start',('conda-recipe.sh',),'postBuild'],
                    meta='meta.yaml',debug=False,\
                    env={'pyver':'3.7'},
                    verbose=True):
    self.verbose  = verbose
    self.meta     = meta
    
    try:
      self.env = getEnv(filename=meta).info
    except:
      if self.verbose:
        print(f'unable to load environment from {meta}')
      self.env = {}
    self.env.update(env)

    self.run_info = []
    for s in scripts:
      # tuple for fatal
      # exit if log is None
      log = self.run_recipe(s,debug=debug)
      if log is None:
        break
      self.run_info.append(log)


  def run_recipe(self,recipe_file,debug=False,fatal=True):
    '''
    read commands recipe from recipe_file
    '''   
    run = not debug
 
    if not Path(recipe_file).expanduser().is_file():
      print('*'*40)
      print(f'{recipe_file} not a file')
      print('*'*40)
      return (not fatal)
    error = None
    retval = []
    env = nested_to_record(self.env,sep="_")
    try:
      if(self.verbose):
        print('*'*40)
        print(recipe_file)
        print('*'*40)

      with open(recipe_file,'r') as f:
        lines = [m for m in [l.strip().split('#')[0] \
                       for l in f.readlines()] if len(m)]   
      # the lines may reference variables from 
      # meta.yaml
      # e.g. requirements.build.python
      for i,m in enumerate(lines):
        # format string them
        m = m.format(**env)
        self.verbose and print(f'** {i+1}/{len(lines)}: {m}')
        if run:
          try:
            retval.append([m,check_output(m,shell=True)])
          except:
            pass
    except:
      error = f'error running {recipe_file}'
      if(fatal):
        for r in retval:
          if(type(r) is str):
            print(r)
          else:
            for rr in r:
              print(rr)
        return not fatal

    if(self.verbose):
      print('#'*40)
      print(f'done {recipe_file}')
      if(error): print(error)
      for r in retval:
          print(r)
      print('#'*40)   
    self.error = error
    return retval

def main(argv):

  verbose = False
  help = False
  recipe = ['start','conda-recipe.sh','postBuild']
  pyver = '3.7'

  env = {"recipe": ["start","conda-recipe.sh","postBuild"]}
  env.update({'pyver':'3.7'})
  env.update({'meta':'meta.yaml'})
  json_env = json.dumps(env) 

  helpstr = f"{sys.argv[0]} [-v|--verbose] [-h|--help]" + "\n" + \
            f"[-e|--env={json_env}]"
  try:
    opts, args = getopt.getopt(argv,"vhe:",["env="])
  except getopt.GetoptError:
    print(helpstr)
    sys.exit(2)
  for opt, arg in opts:
    if opt in ("-v", "--verbose"):
        verbose = True
    elif opt in ('-h','--help'):
        print(helpstr)
        sys.exit()
    elif opt in ('-e','--env'):
        this_env=json.loads(arg)
        env.update(this_env)

  scripts = env['recipe']
  meta    = env['meta']
  del env['recipe']
  del env['meta']

  if (verbose):
    print('scripts',scripts)  
    print('meta',meta)
    print('env',env)

  # convert back json env 
  Batch(scripts=scripts,env=env,meta=meta,verbose=verbose)

def test(tdir='.test'):
  '''
  a test
  '''
  import deepdiff

  tdir = Path(tdir).expanduser()
  tdir.mkdir(parents=True, exist_ok=True)

  return True

if __name__ == "__main__":
  main(sys.argv[1:])

