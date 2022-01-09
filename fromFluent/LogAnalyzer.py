#!/usr/bin/env python

import os, sys
from E_lib import paintText, mkdirs

color = paintText()
internalPaterns = ["NON_ZERO_REFCOUNT_STAT","NON_ZERO_REFCOUNT ","NON_ZERO_REFCOUNT_STAT events"]
#internalPaternsRE = {ptrn:re.compile(ptrn) for ptrn in internalPaterns}
inputPaterns = []
inputPaternsRE = {}
linesFound = {}



def getOptions(argv): # This function will Parse cmdline options
    import optparse
    
    usage = "\t%prog [options] \n\t%prog --help"
    
    options = optparse.OptionParser(usage, version="Rev. 1")
    options.add_option("-l", "--log", action="store", dest="log", default=None, help="log to analyse")
    options.add_option('-d', '--dest', action="store", dest="dest", default='./new/', help='destination of output files (./new/ dir is default)')
    options.add_option('-p', '--patern', action="store", dest="paternStr", default=None, help='patern to search in the log in addition to default paterns')
    options.add_option('-P', '--patern-file', action="store", dest="paternFile", default=None, help='file containing paterns to search in the log in addition to default paterns')
    options.add_option('-w', '--warning', action="store_true", dest="warning", default=False, help='issue warning instead of error when patern from input is found - only for paterns from cmd or fine')
    options.add_option('-i', '--no-internal', action="store_true", dest="internal", default=False, help='do not match internal paterns')
    options.add_option("-v", "--verbose",action="store_true",dest="verbose",default=False, help="Print full output.")
    op, args = options.parse_args()
    
    #--------------------------------------------
    
    if op.log:
        if not os.path.isfile(op.log):
            options.error(color.red('"-l, --log" got invalid path'))
    else:
        raise options.error(color.red('"-l, --log" is not defined.\n'))     
        
    if op.dest == './new/':
        mkdirs(op.dest)
    else:
        if not os.path.isdir(op.dest):
            options.error(color.red('"-d, --dest" got invalid path'))
    if op.paternFile :
        if not os.path.isfile(op.paternFile):
            options.error(color.red('"-P, --patern-file" got invalid path'))
        else:
            with open(op.paternFile,"r") as paternF :
                for patern in paternF:
                    inputPaterns.append(patern.strip())
    if op.paternStr:
        inputPaterns.append(op.paternStr)      
    
    
    return (op, args)

def printList(l):
    for s in l:
        print s


def paternMatchRE(op,paterns):
    import re
    #paterns = internalPaterns + inputPaterns
    paternsRE = {ptrn:re.compile(ptrn) for ptrn in paterns}
    for patern in paterns:
        linesFound[patern] = []
    with open(op.log,"r") as logF :
        for line in logF:
            for patern in paterns:
                if paternsRE[patern].match(line):
                    linesFound[patern].append(line)
                    print patern
                    print line
                    

def paternMatch(op,paterns):
    for patern in paterns:
        linesFound[patern] = []
    with open(op.log,"r") as logF :
        for line in logF:
            for patern in paterns:
                if patern in line:
                    linesFound[patern].append(line)

def paternVerifyEvents(matchList):
    res = True
    for line in matchList:
        if op.verbose: print line
        segment = line.split()
	print segment[-2], segment[-4]
        if int(segment[-2]) <= 4 :
            #to ignore lines like: 20160719-05:16:12.157968 DEBUG_LEVEL NON_ZERO_REFCOUNT_STAT events pool 1 4
            if segment[-4] != "events" :
                warnLevel = "WARNING: "
            else:
                warnLevel = "INFO: "
        else:
            warnLevel = "ERROR: "
            res = False
        print warnLevel + line.split('\n')[0]
        open(op.dest + "matched.res","a").writelines(warnLevel + line)
        
    return res
            
def paternVerifyRefcount(matchList):
    res = True
    for line in matchList:
        if "PRICE_BOOK_BID: - empty - PRICE_BOOK_ASK: - empty" not in line and "EVENT_RATE_DISCONNECT" not in line and "EVENT_TRADE_DISCONNECT" not in line:
            print "ERROR: " +  line.split('\n')[0]
            open(op.dest + "matched.res","a").writelines("ERROR: " + line)
            res &= False
    return res

def inputPaternVerify():
    retVal = True
    warnLevel = ("WARNING: " if op.warning else  "ERROR: ")
    for match in inputPaterns:
        if len (linesFound[match]) > 0 :
            print warnLevel + str(len (linesFound[match])) + " matches fond for " + match
            if op.verbose : printList (linesFound[match])
            open(op.dest + "matched.res","a").writelines(warnLevel + str(len (linesFound[match])) + " matches fond for " + match + '\n')
            open(op.dest + "matched.res","a").writelines(linesFound[match])
            retVal = op.warning
    return retVal

def main(op):
    print "Analyzing log:", op.log
    result = True
    paternMatch(op,inputPaterns + (internalPaterns if not op.internal else []) )
    
    result = inputPaternVerify() 
    if not op.internal :
        for match in internalPaterns:
            #if op.verbose : print match, "\n------\n", linesFound[match]
            if len (linesFound[match]) >= 0 :
                if match == "NON_ZERO_REFCOUNT_STAT events":
                    result &= paternVerifyEvents(linesFound[match]) 
                elif match == "NON_ZERO_REFCOUNT " :
                    result &= paternVerifyRefcount(linesFound[match])
                elif match == "NON_ZERO_REFCOUNT_STAT" :
                    pass
    print "finished analyze with no ERRORS" if result else exit (1)
    
    


 
if(__name__ == "__main__"):
    try:
        op, args = getOptions(sys.argv)
    except Exception, e:
        print >> sys.stderr, e            
        sys.exit(2)
       
    main(op)
