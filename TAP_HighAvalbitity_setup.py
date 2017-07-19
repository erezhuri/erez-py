#!/usr/bin/env python

import sys, os, math, commands, cPickle, time, shutil, tempfile, logging
#sys.path.append("/mobileye/shared/scripts/QA_Bundle_scripts/lib/")
from E_lib import *
color = paintText()

def getOptions(argv): # This function will Parse cmdline options
	import optparse
	
	usage = "\t%prog [options] \n\t%prog --help"
	options = optparse.OptionParser(usage, version='''Version: 0.0
	06/04/2013:
		First revision!
	''')
	mandatoryGroup = optparse.OptionGroup(options, color.red("Mandatory"), "this options must be defined")
	optionalGroup = optparse.OptionGroup(options, "Optional")
	
	mandatoryGroup.add_option("-u", "--setup", action="store", dest="up", default=None, help="setup the env to start testing")
	mandatoryGroup.add_option("-d", "--setback", action="store", dest="back", default=None, help="finish testing - 'setback' the env")
	mandatoryGroup.add_option("-t", "--tunnels", action="store", dest="tunnels", default=None, help="enter list of tunnels to start/stop")
	mandatoryGroup.add_option("-f", "--fxcfg", action="store", dest="FXcfg", default=None, help="enter pathe of the cfg file of FIXation")
	mandatoryGroup.add_option("-c", "--ctrlcfg", action="store", dest="ctrlcfg", default=None, help="enter pathe of the cfg file of Controller")
	optionalGroup.add_option("-v", "--verbose",action="store_true",dest="verbose",default=False, help="Print full output.")
	
	options.add_option_group(mandatoryGroup)
	options.add_option_group(optionalGroup)
	
	(op,args) = options.parse_args()
	
	return (op, args)


def manageCtrlrCFG(op.ctrlcfg):
	pass



def runTunnels (op.tunnels):
	if "solace" in op.tunnels:
		a = commands.getoutput("stunnel solace") #run the tstunnel command for each tunnel in the op.tunnels variable

	elif "fxall" in op.tunnels:
				a = commands.getoutput("stunnel fxall") #run the tstunnel command for each tunnel in the op.tunnels variable

def manageFIXationCFG(cfg):
	manageCFG(cfg, "FIXation")


def manageCFG(cfg, app):
	newcfg = cfg[:-3] + '_HA'+time.strftime("%Y%m%d_%H%M%S")+'.cfg'
	shutil.copy(op.FXcfg, newcfg)
	logging.info("%s new cfg: %s" %(app, newcfg))
	replace(newcfg,old_IP,new_IP)



def replace(source_file_path, pattern, substring):
	fh, target_file_path = tempfile.mkstemp()
	with open(target_file_path, 'w') as target_file:
		with open(source_file_path, 'r') as source_file:
			for line in source_file:
				target_file.write(line.replace(pattern, substring))
	os.remove(source_file_path)
	shutil.move(target_file_path, source_file_path)




def runSetup(op):
	#run all functions for seting up the env to start testing

def runSetback(op):
	#run all functions for seting back the env after testing

def main(op): # This function will run all basic usage of SimFix_Suit_Infrastructure.
	print color.brown("\n\n\t*** TAP - HighAvalability Setup / setback ***\n")
	if op.up:
		runSetup(op)
	elif op.back:
		runSetback(op)

if(__name__ == "__main__"):
	try:
		op, args = getOptions(sys.argv)
	except Exception, e:
		print >> sys.stderr, e			
		sys.exit(2)
	
	# set up logging to file
	logFileName = TAP_HA_+time.strftime("%Y%m%d_%H%M%S")+'.log'
	logging.basicConfig(level=logging.INFO,
			#level=logging.DEBUG
			format='%(asctime)s,%(levelname)-8s,%(message)s',
			#format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
			datefmt='%m-%d %H:%M',
			filename=logFileName,
			filemode='w')
	# define a Handler which writes WARNING messages or higher to the sys.stderr
	console = logging.StreamHandler()
	console.setLevel(logging.WARNING)
	# set a format which is simpler for console use
	formatter = logging.Formatter('%(levelname)-8s: %(message)s')
	# tell the handler to use this format
	console.setFormatter(formatter)
	# add the handler to the root logger
	logging.getLogger('').addHandler(console)


	main(op)
