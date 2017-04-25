#!/usr/bin/env python
# | Copyright 2010-2016 Karlsruhe Institute of Technology
# |
# | Licensed under the Apache License, Version 2.0 (the "License");
# | you may not use this file except in compliance with the License.
# | You may obtain a copy of the License at
# |
# |     http://www.apache.org/licenses/LICENSE-2.0
# |
# | Unless required by applicable law or agreed to in writing, software
# | distributed under the License is distributed on an "AS IS" BASIS,
# | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# | See the License for the specific language governing permissions and
# | limitations under the License.

import argparse
import os,sys



parser = argparse.ArgumentParser(prog='./datasetListFromLS_v2.py', usage='%(prog)s [options]', description="Create a dbs list from LS command")

parser.add_argument("-p", "--path", dest="path", help="Path to the directory your files are stored")
parser.add_argument("-n", "--nick", dest="nickname", help="the nickname you want to the dataset ", default="Dataset")
parser.add_argument("--endswith", dest="endswith", default=".root", help='only select files which endswith "%(default)s"')
parser.add_argument("--maxdepth", dest="maxdepth", default=-1 , help="max depth you want to go with you files")
parser.add_argument("--add_num_events", action='store_true', default=False, dest="addnumevents",help="if true access the files an try to find out how much events are there")
parser.add_argument("--add_lfn", action='store_true', default=False, dest="addlfn",help="if true split the commonprefix by the a lfn mody")
args = parser.parse_args()

if not args.path:
  print "please give provide a path to the root file witht the option -p (--path)"
  sys.exit()

def list_dir(in_dir,full_list,akt_depth=0):
  if int(akt_depth) > int(args.maxdepth) and args.maxdepth >= 0:
    return
  for obj in os.listdir(in_dir):
    full_obj = os.path.join(in_dir,obj)
    if os.path.isdir(full_obj):
      list_dir(full_obj,full_list,akt_depth+1)
    elif obj.endswith(args.endswith):
      full_list.append(full_obj)
      
def get_n_events(in_file):
  if args.addnumevents:
    pass
    print "must be included here"
  return -1
  

def give_dbs_list(file_list,nickname):
  ret_str = ""
  ret_str += "[/PRIVATE/%s]\n"%nickname
  ret_str += "nickname = %s\n"%nickname

  prefix = os.path.dirname(os.path.commonprefix(file_list))
  file_str = ""
  all_events = 0
  for akt_file in file_list:
    akt_events = get_n_events(akt_file)
    all_events +=akt_events
    file_str+=os.path.relpath(akt_file,prefix)+" = %s\n"%str(akt_events)
  ret_str += "events = %s\n"%str(all_events)
  if args.addlfn:
    if prefix.find('/store/') < 0:
      print 'prefix does not include "/store/" string. So it is not possible to determine a lfn for this files '
      ret_str += "prefix = %s\n"%prefix
    else:   
      ret_str += "partition lfn modifier = %s\n"%prefix[:prefix.find('/store/')+1]
      ret_str += "prefix = %s\n"%prefix[prefix.find('/store/'):]
  else:
    ret_str += "prefix = %s\n"%prefix
    
  ret_str+=file_str
  
  return ret_str


files_list = []
list_dir(args.path,files_list)

print give_dbs_list(files_list,args.nickname)


