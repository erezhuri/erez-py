#!/usr/bin/env python 
import sys, os, telnetlib, pyodbc, re, logging #, math, commands, cPickle, datetime, shutil, _mssql,
#sys.path.append("/mobileye/shared/scripts/QA_Bundle_scripts/lib/")
from E_lib import *
color = paintText()


def status_lp(): #host, port ):
	global logFile
	global logPrefix
	if verbose: print color.blue("\t=== Start Status ===")
	telnet.read_until('>',10)
	telnet.write("fs\n")
	response = telnet.read_until('>',10).split('\n')
	lp_list = []
	not_connected = []
	for line in response:
		if "not-connected" in line:
			not_connected.append(line.split()[0])
		elif "connected" in line:
			lp_list.append(line.split()[0])
	
	logging.warning('non-connected LPs: %s ' % ', '.join(not_connected))
	logging.info('connected LPs: %s' % ', '.join(lp_list))
	#logStr = 'non-connected LPs:\n' + ', '.join(not_connected) + '\nconnected LPs:\n' + ', '.join(lp_list)
	#printStr = color.red('non-connected LPs:\n') + ', '.join(not_connected) + color.green('\nconnected LPs:\n') + ', '.join(lp_list)

	#logFile.writelines(logStr)
	#if verbose:	print printStr

	return lp_list


def info_lp(lp_list):
	if verbose: print color.blue("\t=== Start Info ===")
	telnet.read_until('>',10)
	for lp in lp_list :
		#print color.blue("LP: %s" %lp)
		telnet.write("clear\ninfo %s\n"% lp)
		logging.info("LP: %s" %lp)
		LPinfo = telnet.read_until('>',10)
		logging.info(LPinfo)
	if verbose: print color.blue("\t=== End Info ===")

def topOfBook_ccy(ccy):
	telnet.read_until('>',10)
	telnet.write("clear\n")

	


def buildTradeFromDB(LP_list, CCY_list, VWAP ):
	LP_list = "','".join(LP_list)
	CCY_list = "','".join(CCY_list)
	con = _mssql.connect(server='10.0.0.202',user='qa',password='1234567')
	if VWAP:
		BasicQueryString = "SELECT ORDERS FROM dbo.Vwap_Orders_view  WHERE LP IN ('%s') AND CCYPAIR IN ('%s')" %(LP_list, CCY_list)
	else:
		BasicQueryString = "SELECT ORDERS  FROM dbo.Orders_view WHERE LP IN ('%s') AND CCYPAIR IN ('%s')" %(LP_list, CCY_list)
	con.execute_query(BasicQueryString)
	return [row['ORDERS'] for row in con]




def trade_sequential(orders):
	if verbose: print color.blue("\t=== Start Trading ===")
	telnet.read_until('>',3)
	for order in orders:
		#if verbose: print "running order: ", order
		logging.info("running order: %s" %order)
		telnet.write("clear\n")
		response = telnet.read_until('>',10)
		telnet.write("%s\n"% order)
		responseSTR = ''
		while 'COMPLETE' not in response:
			tmp = telnet.read_until('>',10) #.split('\n')
			responseSTR += tmp
			if tmp == '': break
		#print "+++ debug:  \n", response, "--- debug:  \n"
		response = responseSTR.split('\n')
		orderID = ''
		output = False
		for line in response:
			if ("status" in line) and ('*' not in line):
				#print "+++ debug:  \n", line, "--- debug:  \n"
				output = True
				orderID = line.split(',')[1]
				#print "order: " , orderID
				logging.info("order: %s" % orderID)
				orderStatus = line.split(',')[2]
				if '(' in orderStatus:
					orderStatus, orderRes = line.split(',')[2].split('(')
					#print "status: ",orderStatus
					#print "result: ",orderRes[:-1]
					logging.info("status: %s - result: %s" % (orderStatus,orderRes[:-1]))
				else:
					logging.info("status: %s" % orderStatus)
					#print "status: ",orderStatus
			elif 'time' in line :
				if not re.search(r'[0-9]{8}-[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9]{3,6}',line):
					output = True
					logging.warning("time-stamp is wrong: %s" %line)
					#print color.red("time-stamp is wrong: %s" %line)
		
		if output:
			logging.debug(responseSTR)
		else:
			logging.info(responseSTR)
	if verbose: print color.blue("\t=== End Trading ===")

#print telnet.read_until('>',10)
#ccy ="eurusd"
#telnet.write("afr %s \n" % ccy)
##telnet.interact()
#print telnet.read_until('>',10)
##print telnet.read_until('>',10)
#telnet.write(b"exit\n")
#telnet.close()


def getOptions(argv): # This function will Parse cmdline options
	import optparse
	
	usage = "\t%prog [options] \n\t%prog --help"
	
	options = optparse.OptionParser(usage, version='''Version: 0.0
	16/09/2013:
	    First revision!
	''')
	#mandatoryGroup = optparse.OptionGroup(options, color.red("Mandatory"), "this options must be defined")
	#optionalGroup = optparse.OptionGroup(options, "Optional")
	
	options.add_option("-l", "--lp", action="store", dest="lp", default=None, help="list of LPs ")
	options.add_option("-c", "--ccy", action="store", dest="ccy", default=None, help="list of CCY pairs")
	options.add_option("-H", "--host", action="store", dest="host", default="localhost", help="IP or name of the host to connect (default: localhost)")
	options.add_option("-p", "--port", action="store", dest="port", default="60000", help="Port number to connect (default: 60000)")
	options.add_option("-o", "--out", action="store", dest="output", default="./", help="location of the output log (default: local './')")
	options.add_option("-w", "--vwap",action="store_true",dest="vwap",default=False, help="use vwap orders.")
	options.add_option("-v", "--verbose",action="store_true",dest="verbose",default=False, help="Print full output.")
	
	#mandatoryGroup.add_option("-l", "--logs", action="store", dest="logs", default=None, help="path to logs directory")
	#optionalGroup.add_option("-v", "--verbose",action="store_true",dest="verbose",default=False, help="Print full output.")
	
	#options.add_option_group(mandatoryGroup)
	#options.add_option_group(optionalGroup)
	
	(op,args) = options.parse_args()
	
	if not op.lp:
		options.error(color.red('"-l, --lp" is not defined!'))
	else:
		op.lp = open(op.lp,'r').read().replace('\n',' ').split()
	if not op.ccy :
		print color.red('"-c, --ccy" is not defined - using default of 1 ccypar (EUR/USD)')
		op.ccy = ['eurusd']
	else:
		op.ccy = open(op.ccy,'r').read().replace('\n',' ').split()
	
	return (op, args)




def main(op): # This function will run all basic usage of Telnet_Basic_Test.
	print color.brown("\n\n\t*** Telnet - Basic Test ***\n")
	global logFile
	global logPrefix
	telnet.open(op.host, op.port)
	try:
		LP_LIST = status_lp() #op.host,op.port)
				
		info_lp(LP_LIST)
		
		#print "LPs:\n",op.lp
		#print"CCY:", op.ccy
		
		
		#buildTradeFile(LP_LIST,op.ccy)
		#orders = open("orders.list",'r').readlines()
		orders = buildTradeFromDB(LP_LIST,op.ccy, op.vwap)
		trade_sequential(orders)
	
	except KeyboardInterrupt :
			print "\nclosing telnet"

	telnet.close()
	#logFile.close()


if(__name__ == "__main__"):
	try:
		op, args = getOptions(sys.argv)
	except Exception, e:
		print >> sys.stderr, e            
		sys.exit(2)
	#logFile = None
	#logPrefix = ''
	logPrefix = os.path.basename(__file__).split('.')[0]
	logFileName = op.output + logPrefix + '.log'
	#logFile = open(logFileName,'w')

	# set up logging to file - see previous section for more details
	logging.basicConfig(level=logging.INFO,#level=logging.DEBUG
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
	
	# Now, define a couple of other loggers which might represent areas in your
	# application:
	
	#logger1 = logging.getLogger('myapp.area1')
	#logger2 = logging.getLogger('myapp.area2')
	#
	#logger1.debug('Quick zephyrs blow, vexing daft Jim.')
	#logger1.info('How quickly daft jumping zebras vex.')
	#logger2.warning('Jail zesty vixen who grabbed pay from quack.')
	#logger2.error('The five boxing wizards jump quickly.')
	


	verbose = op.verbose
	telnet = telnetlib.Telnet() #op.host, op.port)
	main(op)
 
 
 
 
#def buildTradeFile(lp_list,ccy_list):
#	with open("orders.list",'w') as orders:
#	#orders = open("orders.list",'w')
#		TIF_list = ('ioc', 'fok', 'day')
#		OT_list = ('pq', 'limit', 'market')
#		VOLUMES = ('500000','1m', '3m', '5m', '10m')
#		for lp in lp_list:
#			for ccy in ccy_list:
#				for TIF in TIF_list:
#					for OT in OT_list:
#						for VOL in VOLUMES:
#							orders.write("buy %s %s %s %s %s\n" % (lp, ccy, VOL, TIF, OT))
#							orders.write("sell %s %s %s %s %s\n" % (lp, ccy, VOL, TIF, OT))
#							orders.write("buyv %s %s %s %s %s\n" % (lp, ccy, VOL, TIF, OT))
#							orders.write("sellv %s %s %s %s %s\n" % (lp, ccy, VOL, TIF, OT))
#		#orders.close()

