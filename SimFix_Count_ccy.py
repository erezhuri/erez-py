#!/usr/bin/env python

import sys, os, math, commands, cPickle, datetime, shutil
from E_lib import *
color = paintText()

def getOptions(argv): # This function will Parse cmdline options
    import optparse
    
    usage = "\t%prog [options] \n\t%prog --help"
    
    options = optparse.OptionParser(usage, version='''Version: 0.0
    16/09/2013:
        First revision!
    ''')
    #mandatoryGroup = optparse.OptionGroup(options, color.red("Mandatory"), "this options must be defined")
    #optionalGroup = optparse.OptionGroup(options, "Optional")
    
    options.add_option("-l", "--list", action="store", dest="list", default=None, help="path to logs list file")
    options.add_option("-L", "--log", action="store", dest="log", default=None, help="path of a logs file")
    options.add_option("-e", "--prinAtEnd",action="store_true",dest="prinAtEnd",default=False, help="Print only when finshed the run on all logs - default False.")
    options.add_option("-v", "--verbose",action="store_true",dest="verbose",default=False, help="Print full output.")

    #mandatoryGroup.add_option("-l", "--logs", action="store", dest="logs", default=None, help="path to logs directory")
    #optionalGroup.add_option("-v", "--verbose",action="store_true",dest="verbose",default=False, help="Print full output.")
    
    #options.add_option_group(mandatoryGroup)
    #options.add_option_group(optionalGroup)
    
    (op,args) = options.parse_args()
    
    if op.log: #Mandatory field
        if op.list:
            options.error(color.red('"-L, --log" and "-l,--list" cannot be set together'))
        if not os.path.isfile(op.log) :
            options.error(color.red('"-L, --log" got invalid path'))
    else:
        if op.list:
            if not os.path.isfile(op.list) :
                options.error(color.red('"-l, --list" got invalid path'))
        else:
            options.error(color.red('nither "-L, --log" nor "-l,--list" was defined.'))

    return (op, args)

def insertToStr(original, new, pos):
    # Inserts new inside original at pos.
    return original[:pos] + new + original[pos:]

def countCCY(log):
    import re
    with open(log,'r') as logLines:    # go into each log file
        for line in logLines:          # go over each log
            pair = re.search(r'55=[A-Z]{3}/?[A-Z]{3}',line)    # find the ccypair in the log line if there is
            #if not pair:
            #    pair = re.search(r'^A55=[A-Z]{3}/[A-Z]{3}^A',line)
            if pair:
                pair = pair.group(0)[4:-1]
                if pair[3] != '/':
                    pair = insertToStr(pair,'/',3)
                if not ccy.get(pair):
                    if not prinAtEnd: print pair
                ccy [pair] = True


def loopFiles(logList):
    with open(logList,'r') as list:    # Open list file
        for log in list:               # go over each log file
            if log[-1] == '\n':log = log[:-1]    # remove endl if exist
            if log.find('#') != -1: continue     # ignore commented lines
            if verbose: print color.blue("counting") , log    # print to screen if verbose=True
            countCCY(log) 

def main(op): # This function will run all basic usage of SimFix_Count_ccy.
    print color.brown("\n\t*** SimFix - count ccy ***\n")
    if op.list:
        loopFiles(op.list)
    if op.log:
        countCCY(op.log)
    if prinAtEnd:
        print color.brown("\t*** SimFix - final results ***")
        for key in ccy:
            print key
    print color.brown("\n\t*** SimFix - Done ***\n")

if(__name__ == "__main__"):
    try:
        op, args = getOptions(sys.argv)
    except Exception, e:
        print >> sys.stderr, e            
        sys.exit(2)

    ccy = {}
    verbose = op.verbose
    prinAtEnd = op.prinAtEnd
    main(op)
    
    
    
