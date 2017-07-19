#!/usr/bin/python

import sys
import os
import random
import re
from collections import defaultdict

import read_cfg

sc_fields = defaultdict(int)
map_mapi_sc = defaultdict(int)
only_mapi = []


if len(sys.argv) != 4:
  print
  print "Usage: %s <left file> <right file> <cfg file>" % sys.argv[0]
  print
  exit(1)

(_,left, right, cfg_file) = sys.argv

list_fix_grouping = []
list_fix_grouping = read_cfg.read_main_OT_cfg(cfg_file)


# here dictionary is:
# key = tag number.       
# value = index row location in right message.
# if tag appears more than once, value will be list of all line numbers this tag appear.
with open (right, "r") as fin:

  i = 1

  for line in fin:
    r =re.search(r'^(\s+?)(\d+)', line)

    try:
      x = r.group(2)
    except AttributeError:
      print "tag was not found, maybe an empty line, skip to the next line"
      continue

    if x in list_fix_grouping and sc_fields[x] == 0:
      sc_fields[x] = [str(i)]
    elif x in list_fix_grouping:
      sc_fields[x].append(str(i))
    else:
      sc_fields[x] = str(i)

    i += 1

print sc_fields

# we are trying match between left and right text
# if we have same tag number in both left and right, we place line of left in location of right
# if tag exists in right and not in left, left result will place empty row
with open (left, "r") as fin:

  for line in fin:
    r =re.search(r'^(\s+?)(\d+)', line)

    try:
      x = r.group(2)
    except AttributeError:
      print "tag was not found, maybe an empty line, skip to the next line"
      continue

# add condition to solve scenario list in left and not in right.
# when left is list and right is empty --> will be added to extra left lines (at the bottom of output)
# when result exists and it is regular (not a list) --> there is much --> will be added to the left main list.
# when result exists and it is list --> there is much --> will be added to the left main list as list (grouping).
    i = sc_fields[x] 
    if type(i) == list and len (i) > 0:
      map_mapi_sc[str(i[0])] = line
      del sc_fields[x][0]
    elif i != 0 and type(i) != list:
      map_mapi_sc[str(i)] = line
    else:
      only_mapi.append(line)

for i in range (1, 90):
  if map_mapi_sc[str(i)] != 0:
    print map_mapi_sc[str(i)],
  else:
    print

# rest of tags, exists in right and not in left, will be 
# printed at the bottom of left output file.
print "follow are tags exists in left side and not in right side"
print "---------------------------------------------------------"

for tag in only_mapi:
  print tag,
