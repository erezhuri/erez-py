#!/usr/bin/env python 
import sys, os, telnetlib, _mssql, re, logging #, math, commands, cPickle, datetime, shutil
#sys.path.append("/mobileye/shared/scripts/QA_Bundle_scripts/lib/")
from E_lib import *
color = paintText()



def buildTradeFromDB(LP_list, CCY_list, VWAP, outFile ):
	LP_list = "','".join(LP_list)
	CCY_list = "','".join(CCY_list)
	con = _mssql.connect(server='10.0.0.202',user='qa',password='1234567')
	if VWAP:
		BasicQueryString = "SELECT ORDERS FROM dbo.Vwap_Orders_view  WHERE LP IN ('%s') AND CCYPAIR IN ('%s')" %(LP_list, CCY_list)
	else:
		BasicQueryString = "SELECT ORDER_ID, ORDERS FROM dbo.Supported_Orders_view WHERE LP IN ('%s') AND CCYPAIR IN ('%s')" %(LP_list, CCY_list)
	con.execute_query(BasicQueryString)
	ordersToRun = [(int(row['ORDER_ID']),row['ORDERS']) for row in con]
	with open(outFile,'w') as out:
		out.write("DB_order_ID,ORDER\n")
		for item in ordersToRun:
			out.write("%s,%s\n" % item)
	return ordersToRun #[(int(row['ORDER_ID']),row['ORDERS']) for row in con]


def readOrdersFromFile(inFile):
	with open(inFile,'r') as ordersF:
		tmp = ordersF.readline()
		if tmp != "DB_order_ID,ORDER\n":
			logger.error("file not match expected format")
			return
		ordersToRun = []
		for line in ordersF:
			order = line[:-1].split(',') if line[-1] == '\n' else line.split(',')
			order[0] = int(order[0])
			ordersToRun.append(tuple(order))
	return ordersToRun



def pushTestResults(testResult):
	con = _mssql.connect(server='10.0.0.202',user='qa',password='1234567')
	for RunID,DBOrderID,ResultsID,LPLog,InterfaceLog in testResult:
		QueryString = "exec dbo.Receive_TestResults @RunID=%d, @DBOrderID=%d, @ResultsID=%d, @LPLog='%s', @InterfaceLog='%s' " %(RunID, DBOrderID, ResultsID, LPLog, InterfaceLog)
		print QueryString
		con.execute_query(QueryString)




def getOptions(argv): # This function will Parse cmdline options
	import optparse
	
	usage = "\t%prog [options] \n\t%prog --help"
	
	options = optparse.OptionParser(usage, version='''Version: 0.0
	24/03/2014:
	    First revision!
	''')
	#mandatoryGroup = optparse.OptionGroup(options, color.red("Mandatory"), "this options must be defined")
	#optionalGroup = optparse.OptionGroup(options, "Optional")
	
	options.add_option("-l", "--lp", action="store", dest="lp", default=None, help="list of LPs (default: all LPs)")
	options.add_option("-c", "--ccy", action="store", dest="ccy", default=None, help="list of CCY pairs (default: EUR/USD)")
	#options.add_option("-H", "--host", action="store", dest="host", default="localhost", help="IP or name of the host to connect (default: localhost)")
	options.add_option("-p", "--push", action="store_true", dest="push", default=False, help="Push results to DB")
	options.add_option("-a", "--action", action="store", dest="action", default="pre", help="Action to run: pre-generate orders to run ,post-run matching on the results and push to DB (default: pre)")
	options.add_option("-o", "--out", action="store", dest="output", default="./", help="location of the output log (default: local './')")
	options.add_option("-w", "--vwap",action="store_true",dest="vwap",default=False, help="use vwap orders.")
	options.add_option("-v", "--verbose",action="store_true",dest="verbose",default=False, help="Print full output.")
	
	#mandatoryGroup.add_option("-l", "--logs", action="store", dest="logs", default=None, help="path to logs directory")
	#optionalGroup.add_option("-v", "--verbose",action="store_true",dest="verbose",default=False, help="Print full output.")
	
	#options.add_option_group(mandatoryGroup)
	#options.add_option_group(optionalGroup)
	
	(op,args) = options.parse_args()
	
	if op.lp:
		op.lp = open(op.lp,'r').read().replace('\n',' ').split()
	if not op.ccy :
		print color.red('"-c, --ccy" is not defined - using default of 1 ccypar (EUR/USD)')
		op.ccy = ['eurusd']
	else:
		op.ccy = open(op.ccy,'r').read().replace('\n',' ').split()
	
	return (op, args)




def main(op): # This function will run all basic usage of Telnet_Basic_Test.
	print color.brown("\n\n\t*** TAP - Bartender ***\n")
	try:
		
		if not op.push:
			buildTradeFromDB(op.lp,op.ccy, op.vwap, op.output + "TAP-ordersToRun.csv")
			orders = readOrdersFromFile(op.output + "TAP-ordersToRun.csv")

			executedOrdersToFile(executedOrders, op.output + "executedOrdersFile.csv")
		else:
			testResult = [[1,2,0,"test1","test2"],[0,0,0,"test3",""]]
			pushTestResults(testResult)


	except KeyboardInterrupt :
			print "\nclosing"



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
 
 
 

