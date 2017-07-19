#!/usr/bin/env python

RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
CYAN = '\033[96m'
WHITE = '\033[97m'
YELLOW = '\033[93m'
MAGENTA = '\033[95m'
GRAY = '\033[90m'
ENDC = '\033[0m'


import argparse
import sys
import fileinput
from collections import defaultdict
import re


parser = argparse.ArgumentParser()
parser.add_argument("--tags", "-t", help = "list of tag numbers separated by comma f.e. 35,269,15 OR -fix patteren- f.e. 35=8")
parser.add_argument("files", metavar="file", nargs="*")
args = parser.parse_args()



# map in table tag number into color
# first tag will be RED
# second tag will be green
# third tag will be blue
# etc.
tag_list = args.tags.split(',')

tagTOcolor = defaultdict(str)
color_list = (RED, GREEN, BLUE, CYAN, YELLOW, MAGENTA, GRAY)

i = 0
for tag_num in tag_list:
    tagTOcolor[str(tag_num)] = color_list[i]
    i += 1



# this function will color specific patterns in a given line
# either arg is to color per tag number - each tag number will be colored with its value
# or by givven whole apttern - in this case pattern will be colored,
# only when match whole patteren.
def color_given_line (line):
  line_arr = []
  res_line = re.sub(r'\x01', ' ', line)
  line_arr = res_line.split ()

  for tag in line_arr:
    if tagTOcolor[tag] != '':
      color_index = tag
    else:
      color_index = tag.split('=')[0]
    print tagTOcolor[color_index] + tag + ENDC,
  print


# if we want to process on stream coming from pipe (stdin)
# we must redirect in args using "-"
if "-" in sys.argv:
  try:
    buff = ''
    while True:
      buff += sys.stdin.read(1)
      if buff.endswith('\n'):
        color_given_line (buff)
        buff = ''
  except KeyboardInterrupt:
    sys.stdout.flush()
    pass

# this will process for given filname
for line in fileinput.input(args.files):
  color_given_line (line)
