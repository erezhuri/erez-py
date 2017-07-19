#!/usr/bin/python

import re

###############################################
#
#          read cfg
#          --------
#
# parse OT
# parse tags
# now we have variable = OT and list = list tags for this OT
#
# run function with above args
#
###############################################

# parse detail according to reg. exp.
############################
## get cfg line type      ##
############################
def get_cfg_line_type (line):
  if re.search(r'^message_type=', line):
    return 0
  if re.search(r'^\s+[A-Za-z]', line):
    return 1
  if re.search(r'^[\s#]+#?', line):
    return 2





############################
## read main cfg OT       ##
############################
# when reach empty line in cfg, create OT, 
# clear OT and tags for next reading.
def read_main_OT_cfg(cfg_file):
  tag_list = []
  msg_type = ''
  value = ''

  with open (cfg_file, 'r') as fin:
    for line in fin:
      res = get_cfg_line_type (line)      
      if res == 2:
        tag_list = []
        msg_type = ''
      elif res == 0:
        msg_type_line = line.strip().split("=")
        value = msg_type_line[1]
      elif res == 1 and value == 'AE':
        tag_line = line.strip().split("=")
        tag_list = tag_line[1].split(",")
        return tag_list
