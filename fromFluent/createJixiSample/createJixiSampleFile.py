#!/usr/bin/python

# bsad

###########################################################################################################################


# This script perform:

# 1) base Jixi sample is taken as arg as the most updated version.
# 2) read cfg and takes relevant Order Types.
# 3) from base Jixi, build header and footer (common for all permotations).
# 4) for each OT, create new base file (based on the new Jixi given arg.)
# 5) for each OT, builds all permotations (for example day-init, fok-init, day-random, fok-random).
# 6) append all builded files into new Jixi sample (i.e. header, day-init, fok-init, day-random, fok-random, footer).


###########################################################################################################################

import re
import os 
import sys
import tempfile
import shutil

if len(sys.argv) != 3:
  print "Usage: ./createJixiSampleFile.py <cfg file> <Jixi Order Sample Updated File>."
  exit(1)

(_, cfg, JixiOrder) = sys.argv


limitTifDict = {'day' : 'TIMEINFORCE_DAY', 'gtc' : 'TIMEINFORCE_GOODTILLCANCEL', 'ioc' : 'TIMEINFORCE_IMMEDIATEORCANCEL', 'fok' : 'TIMEINFORCE_FILLORKILL'}

pegSideDict = {'bid' : 'PRICE_SIDE_BID', 'ask' : 'PRICE_SIDE_OFFER', 'midpoint' : 'PRICE_SIDE_MIDPOINT', 'market_peg': 'PRICE_SIDE_MARKET_PEG', 'primary' : 'PRICE_SIDE_PRIMARY'}

pegOffsetType = {'pip' : 'OFFSET_PIP', 'percent': 'OFFSET_PERCENT'}

displayMethodDict = {'init' : 'DISPLAY_METHOD_INITIAL', 'random' : 'DISPLAY_METHOD_RANDOM'}

my_dir = tempfile.mkdtemp()

shutil.copy(JixiOrder, my_dir + "/")

head, tail = os.path.split(JixiOrder)

JixiOrder = my_dir + "/" + tail     

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
  if re.search(r'^ot=', line):
    return 0
  if re.search(r'^\s+[A-Za-z]', line):
    return 1
  if re.search(r'^[\s#]+#?', line):
    return 2


############################
## read tags              ##
############################
def read_tags (ot, alltags = {}):
  tif = {}
  max_slice = {}
  display_method = {}
  interval = {}
  peg_side = {}
  offset = {}
  offset_type = {}
  discrt = {}
  protect = {}
  if ot == '':
    return 0
  else:
    if ot == 'iceberg':
      tif = alltags['tif'].split(',')
      max_slice = alltags['max_slice'].split(',')
      display_method = alltags['display_method'].split(',')
      interval = alltags['interval'].split(',')
      iceberg(tif, max_slice, display_method, interval)
    if ot == 'peg':
      tif = alltags['tif'].split(',')
      peg_side = alltags['peg_side'].split(',')
      offset = alltags['offset'].split(',')
      offset_type = alltags['offset_type'].split(',')
      discrt = alltags['discrt'].split(',')
      protect = alltags['protect'].split(',')
      peg(tif, peg_side, offset, offset_type, discrt, protect)
    if ot == 'market':
      tif = alltags['tif'].split(',')
      market(tif)
    if ot == 'limit':
      tif = alltags['tif'].split(',')
      limit(tif)
  pass


############################
## read main cfg OT       ##
############################
# when reach empty line in cfg, create OT, 
# clear OT and tags for next reading.
def read_main_OT_cfg():
  tag_list = {}
  ot = ''

  with open (cfg, 'r') as fin:
    for line in fin:
      res = get_cfg_line_type (line)      
      if res == 2:
        read_tags (ot, tag_list)
        tag_list = {}
        ot = ''
      elif res == 0:
        ot_line = line.strip().split("=")
        ot = ot_line[1]
      elif res == 1:
        tag_line = line.strip().split("=")
        tag_name = tag_line[0]
        tag_list[tag_name] = tag_line[1]
  





############################
###### build header  #######
############################
# build headr from most updated
# Java file arrived as arg. from 
# command line
def build_header(JixiOrder):
  with open (JixiOrder, 'r') as fin:
    with open (my_dir + "/JixiSampleHeader.txt", 'w') as fout:
        for line in fin:
          if re.search(r'/////////////////////////////////////PQ ORDER////////////////////////////////////', line):
            break
          fout.write(line) 
        for _ in range (10):
          fout.write("              //////////////////////////////////////////////////////////////////////////////////\n") 
        fout.write("\n") 
        fout.write("              ///////////////////           PRE DEFINITION      ////////////////////////////////\n") 
        fout.write("                JixiOrderParams ordParms;\n") 
        fout.write("                int rc=0;\n") 
        fout.write("              //////////////////////////////////////////////////////////////////////////////////;\n") 
          

############################
###### build footer  #######
############################
# build footer from most updated
# Java file arrived as arg. from 
# command line
def build_footer(JixiOrder):
  with open (JixiOrder, 'r') as fin:
    with open (my_dir + "/JixiSampleFooter.txt", 'w') as fout:
        fout.write("\n") 
        fout.write("\n") 
        fout.write("\n") 
        fout.write("\t\t}\n") 
        fout.write("\t}\n") 
        allowCopy = False
        for line in fin:
          if re.search(r'void printBook', line):
            allowCopy = True
          if allowCopy is True:
            fout.write(line) 


################################
###### build OT base file ######
################################
# build peg OT from most updated
# Java file arrived as arg. from 
# command line
def build_OT_base_file(JixiOrder, OT_name):
  OT_dict = {'peg' : 'PEG ORDER', 'iceberg' : 'ICEBERG ORDER', 'limit' : 'LIMIT ORDER', 'market' : 'MARKET ORDER'}
  with open (JixiOrder, 'r') as fin:
    with open (my_dir + "/" + OT_name + ".txt", 'w') as fout:
        fout.write("\n") 
        allowCopy = False
        
        for line in fin:
          if re.search(r"/+?\s*?%s\s*?/+?" % OT_dict[OT_name], line):
            allowCopy = True
          elif re.search(r'//////////////////////////////////////////////////////////////////////////////////', line) and allowCopy is True:
            fout.write(line) 
            fout.write("\n") 
            fout.write("\n") 
            allowCopy = False
          if allowCopy is True:
            fout.write(line) 



############################
######  MARKET       #######
############################
def market(tif_list={}):
  build_OT_base_file(JixiOrder, 'market')
  for tif in tif_list:
    with open (my_dir + "/" + 'market' + ".txt", 'r') as fin:
      mrk = 'market' + tif
      with open (mrk, 'w') as fout:
        for line in fin:
          line_tif = re.sub(r'TIMEINFORCE_IMMEDIATEORCANCEL', limitTifDict[tif], line)
          fout.write(line_tif)
      
    filenames.append(mrk)



############################
######  LIMIT        #######
############################
def limit(tif_list={}):
  build_OT_base_file(JixiOrder, 'limit')
  for tif in tif_list:
    with open (my_dir + "/" + 'limit' + ".txt", 'r') as fin:
      lmt = 'limit' + tif
      with open (lmt, 'w') as fout:
        for line in fin:
          line_tif = re.sub(r'TIMEINFORCE_IMMEDIATEORCANCEL', limitTifDict[tif], line)
          fout.write(line_tif)
      
    filenames.append(lmt)



############################
######  ICEBERG      #######
############################
def iceberg(tif_list={}, slice_list={}, display_method_list={}, interval_list={}):
  build_OT_base_file(JixiOrder, 'iceberg')
  for tif in tif_list:
    for slc in slice_list:
      for display_method in display_method_list:
        for interval in interval_list:
	  with open (my_dir + "/" + 'iceberg' + ".txt", 'r') as fin:
	    ice = tif + slc + display_method + interval
	    with open (ice, 'w') as fout:
	      for line in fin:
		if re.search(r'TIMEINFORCE_IMMEDIATEORCANCEL', line):
		  line_tif = re.sub(r'TIMEINFORCE_IMMEDIATEORCANCEL', limitTifDict[tif], line)
		  fout.write(line_tif)
		elif re.search(r'setMaxSliceVolume', line):
		  line_tif = re.sub(r'1000000', slc, line)
		  fout.write(line_tif)
		elif re.search(r'DisplayMethod', line):
		  line_tif = re.sub(r'DISPLAY_METHOD_RANDOM', displayMethodDict[display_method], line)
		  fout.write(line_tif)
		elif re.search(r'setMaxIntervalTime', line):
		  line_tif = re.sub(r'5', interval, line)
		  fout.write(line_tif)
		else:
		  fout.write(line)
	  filenames.append(ice)




############################
######     PEG       #######
############################
# build sub-peg-OT file for each permotation
# for example, if we have two TIF (day and gtc) and two peg-type (bid and ask)
# you will get 4 'files':
# 1. day bid
# 2. day ask
# 3. gtc bid
# 4. gtc ask
#####################################################################################
def peg(tif_list={}, peg_side_list={}, offset_list={}, offset_type_list={}, discrt_list={}, protect_list={}):
  build_OT_base_file(JixiOrder, 'peg')
  for tif in tif_list:
    for peg_side in peg_side_list:
      for offset in offset_list:
	for offset_type in offset_type_list:
	  for discrt in discrt_list:
	    for protect in protect_list:
	      with open (my_dir + "/" + 'peg' + ".txt", 'r') as fin:
		peg = my_dir + "/" + tif + peg_side + offset + offset_type + discrt + protect
		with open (peg, 'w') as fout:
		  for line in fin:
		    if re.search(r'TIMEINFORCE_DAY', line):
		      line_tif = re.sub(r'TIMEINFORCE_DAY', limitTifDict[tif], line)
		      fout.write(line_tif)
		    elif re.search(r'PriceSideType', line):
		      line_tif = re.sub(r'PRICE_SIDE_PRIMARY', pegSideDict[peg_side], line)
		      fout.write(line_tif)
		    elif re.search(r'setOffset\b', line):
		      line_tif = re.sub(r'10', offset, line)
		      fout.write(line_tif)
		    elif re.search(r'setOffsetType\b', line):
		      line_tif = re.sub(r'OFFSET_PERCENT', pegOffsetType[offset_type], line)
		      fout.write(line_tif)
		    elif re.search(r'setDiscretion\b', line):
		      line_tif = re.sub(r'5', discrt, line)
		      fout.write(line_tif)
		    elif re.search(r'setProtection\b', line):
		      line_tif = re.sub(r'10', protect, line)
		      fout.write(line_tif)
		    else:
		      fout.write(line)
	      filenames.append(peg)




#######################################################

build_header(JixiOrder)
filenames = [my_dir + '/JixiSampleHeader.txt']
      
read_main_OT_cfg()

build_footer(JixiOrder)
filenames.append(my_dir + '/JixiSampleFooter.txt')




    





# now collect all files
# header + OT1 + OT2 + OY3 ... + footer
# and build JixiOrdersSample.java
with open ("JixiOrdersSample.java", 'w') as fout:
  for fname in filenames:
    with open (fname, 'r') as fin:
      for line in fin:
        fout.write(line)


shutil.rmtree(my_dir)
