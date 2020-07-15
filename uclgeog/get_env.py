#!/usr/bin/env python

  

__author__ = "P Lewis"
__copyright__ = "Copyright 2020 P Lewis"
__license__ = "GPLv3"
__email__ = "p.lewis@ucl.ac.uk"

import yaml
import json
import os
import sys
import getopt
from pathlib import Path

class getEnv():
  '''
  Utility to get environment variables
  from-to various format
  takes setup dictionary variable if it exists.
  '''
  def __init__(self,filename=None,initial=None,override=None,\
                    upper=False,export=True,stripstr='"'):
    '''
    Read environments from yaml, json 
    or bash environment

    Start with initial
    Override with dictionary override

    Write to yaml, json 
    or bash environment

    Options:

      filename=None  : filename to read data from
      initial=None   : initial dictionary
      override=None  ~: override dictionary

      Any of these can be None (so {}), but the logig is that
      override over-rides filename over-rides initial 

      For bash env:

        upper=False  : if set True, key names converted to lower case on read
                       (to be consistent with conversion to upper on write)
        export=True  : if set True, write bash op as "export KEY=VALUE" 

    '''
    self.upper = upper
    self.initial = initial or {}
    self.override = override or {}
    self.filename = filename
    self.export = export

    self.info = self.initial.copy()  
    # get info from file 
    self.read_info = (self.filename and self.get_load(self.filename,stripstr=stripstr)) or {}
    self.info.update(self.read_info)
    self.info.update(self.override)

  def write(self,filename,append=True,tidy=False):
    '''
    Write the info in self.info to filename.

    The type is determined by the suffix.

    Options:
      append=True :  add this to the existing information
                     over-riding what may be there
      tidy=False  :  flag to try to tidy up file in case of
                     multiple entries (as in multiple lines of the same
                     thing in a bash file). NOT IMPLEMENTED

    Also:
      self.export=True :  add 'export' to env if bash
      
    '''
    filename = Path(filename).expanduser()
    suffix = filename.suffix.lower()
    
    if (suffix == '.yml') or (suffix == '.yaml'):
      info = (append and self.get_load(filename)) or {}
      info.update(self.info)
      with open(filename,'w') as f:
        yaml.dump(info,f)
    elif (suffix == '.jsn') or (suffix == '.json'):
      info = (append and self.get_load(filename)) or {}
      info.update(self.info)
      with open(filename,'w') as f:
        json.dump(info,f)

    else:
      # convert dict to env list
      env = self.convert_to_env(self.info)
      with open(filename,(append and 'a') or 'w') as f:
        for l in env:
          f.writelines(l)

  def convert_to_env(self,info,nl=True):
    ''' 
    convert dictionary info (1-deep) from info into
    list of bash env strings

    options:
      nl  : add newline to each (default True)

    e.g.
    self.export=False
    self.convert_to_env({'hello': 'world'})
    [['hello=world\n']]

    e.g.
    self.export=True
    self.convert_to_env({'hello': 'world'})
    [['export hello=world\n']]

    e.g.
    self.upper = True
    self.convert_to_env({'hello': 'world'})
    [['export HELLO=world\n']]

    '''
    nl = (nl and '\n') or ''
    pre = (self.export and 'export ') or ''
    return [f'{pre}{self.upper and k.upper() or k}={v}{nl}' for k,v in info.items()]
  
  def get_load(self,filename,stripstr='"'):
    '''
    load as implied by filename
    else, assume its a text file containing 
    env variables of the form

      KEY=VALUE

    or
 
      export KEY=VALUE

    It is non-strict on spaces (unlike bash)

      self.upper=False  : if set True, key names converted to lower case on read
                          (to be consistent with conversion to upper on write)
    '''
    filename = Path(filename).expanduser()
    suffix = filename.suffix.lower()
    retval = {}
    # return retval isd not exist
    if not filename.exists():
      return retval

    with open(filename,'r') as f:
      if (suffix == '.yml') or (suffix == '.yaml'):
        retval = yaml.safe_load(f)
      elif (suffix == '.jsn') or (suffix == '.json'):
        retval = json.load(f)
        
      else:
        # some sort of bash-type env, with '=' sep and # comments
        retval1 = [i.strip().split('#')[0] for i in f.readlines()]
        retval = {}
        for i in retval1:
          # remove any export
          f = i.find('export ')
          if f >= 0:
            i = i[len('export ')+f:]
          # split on first =
          f = i.find('=') 
          if f > 0:
            key       = i[:f].strip()
            value_str = i[f+1: ].strip() 
            value = json.loads(value_str.replace("'",'"'))
            retval[key] = value
          else:
            # not sure we want to be here`??
            # so lump it in anyway
            retval['no_key'] = i

        # lower-case the keys
        if self.upper:
          for k in retval.keys():
            value = retval[k]
            del retval[k]
            retval[k.lower()] = value

        # now, look for sub-dictionaries
        for k,v in retval.items():
          if type(v) is str:
            retval[k] = self.get_dict(v) 


    return retval

# for test
meta_yaml = '''
# ipypi and conda parameters
# 
package:
  name:    uclgeog
  version: 1.0.0

source:
  git_rev: 1.0.0
  git_url: https://github.com/UCL-EO/uclgeog

build:
  noarch: python
  number: 0
  script: python -m pip install --no-deps --ignore-installed .


requirements:
  build:
    - python>=3.7
    - setuptools

  run:
    - python

test:
  imports:
    - gdal

about:
  home:         https://github.com/UCL-EO/uclgeog
  description:  UCL Geography course notes
  author:       Prof. P. Lewis
  email:        p.lewis@ucl.ac.uk
  keywords:     scientific computing
  license:      MIT

docker:
  user:         proflewis
  tag:          latest
  nb_user:      uclgeog

'''

def main(argv):

  ifile=None
  initial=None
  override=None
  upper=False
  export=False
  ofile=None
  verbose=False
  convert_to_env=False
  append=True

  help = False
  helpstr = f"{sys.argv[0]} [-e|--export] [-v|--verbose] [-h|--help]" + "\n" + \
            "[-I|--initial=initial.sh] [-O|--override=override.sh]" + "\n" + \
            "[-i|--ifile=input.sh] [-o|--ofile=ofile.sh]" + "\n" + \
            "[-t | --test] [-a|--append or -w|--write] [-c|--convert_to_env]"
  try:
    opts, args = getopt.getopt(argv,"twcavi:I:o:O:eu",["ifile=","initial=","ofile=","override="])
  except getopt.GetoptError:
    print(helpstr)
    sys.exit(2)
  for opt, arg in opts:
    if opt in ("-i","--ifile"):
       ifile=arg
    elif opt in ("-I","--initial"):
       initial=arg
    elif opt in ("-O","--override"):
       override=arg
    elif opt in ("-o","--ofile"):
       ofile=arg
    elif opt in ("-t", "--test"):
       test();
       sys.exit()
    elif opt in ("-v", "--verbose"):
        verbose = True
    elif opt in ('-u','--upper'):
        upper = True
    elif opt in ('-a','--append'):
        append = True
    elif opt in ('-w','--write'):
        append = False
    elif opt in ('-e','--export'):
        export = True
    elif opt in ('-h','--help'):
        print(helpstr)
        sys.exit()
    elif opt in ('-c','--convert_to_env'):
        convert_to_env = True
 
  # read files
  if verbose and initial:
    print(f"reading initial from {initial}")
  initial = (initial and getEnv(filename=initial,upper=upper,export=export).info) or {}

  if verbose and override:
    print(f"reading override from {override}")
  override = (override and getEnv(filename=override,upper=upper,export=export).info) or {}

  if verbose and ifile:
    print(f"reading data from {ifile}")
  env = getEnv(filename=ifile,upper=upper,export=export,override=override,initial=initial) 

  if verbose and ofile:
    print(f"writing to ofile\nappend={append}")
  ofile and env.write(ofile,append=append)

  # maybe pretty this
  if verbose:
    if convert_to_env:
      print('converting to env')
      print(env.convert_to_env(env.info));
    else:
      print('printing dictionary')
      print(env.info);

def test(tdir='.test'):
  '''
  a test
  '''
  import deepdiff

  tdir = Path(tdir).expanduser()
  tdir.mkdir(parents=True, exist_ok=True)

  ifile_yml = 'input_test1.yml'
  tfile = tdir.joinpath(ifile_yml)
  # write meta_yaml
  with open(tfile,'w') as f:
    f.writelines(meta_yaml)

  # now read it
  result1 = getEnv(filename=tfile)

  ofile_yml = 'test1.yml'
  tfile = tdir.joinpath(ofile_yml)
  # write result1 to yml
  result1.write(tfile,append=False)

  ofile_json = 'test1.json'
  tfile = tdir.joinpath(ofile_json)
  # write result1 to json
  result1.write(tfile,append=False)

  ofile_sh = 'test1.sh'
  tfile = tdir.joinpath(ofile_sh)
  # write result1 to sh
  result1.write(tfile,append=False)

  # read
  result1_yml = getEnv(filename=tdir.joinpath(ofile_yml)).info
  result1_sh  = getEnv(filename=tdir.joinpath(ofile_sh)).info
  result1_jsn = getEnv(filename=tdir.joinpath(ofile_json)).info

  try:
    # see if yaml and json are the same
    assert deepdiff.DeepDiff(result1_yml,result1_jsn) == {}
  except AssertionError as error:
    print('AssertionError: see if yaml and json are the same',error)
    print(deepdiff.DeepDiff(result1_yml,result1_jsn))
    print('='*40)
    print(tdir.joinpath(ofile_yml))
    print('='*40)
    print(result1_yml)
    print('='*40)
    print(tdir.joinpath(ofile_jsn))
    print('='*40)
    print(result1_jsn) 
  except Exception as exception:
    print('Exception: see if yaml and json are the same',exception)

  try:
    # see if yaml and sh are the same
    assert deepdiff.DeepDiff(result1_yml,result1_sh) == {}
  except AssertionError as error:
    print('AssertionError: see if yaml and sh are the same',error)
    print(deepdiff.DeepDiff(result1_yml,result1_sh))
    print('='*40)
    print(tdir.joinpath(ofile_yml))
    print('='*40)
    print(result1_yml)
    print('='*40)
    print(tdir.joinpath(ofile_sh))
    print('='*40)
    print(result1_sh)    
  except Exception as exception:
    print('Exception: see if yaml and sh are the same',exception)

  return True

if __name__ == "__main__":
  main(sys.argv[1:])

