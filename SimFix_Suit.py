#!/usr/bin/env python

import sys, os, math, commands, cPickle, datetime, shutil
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
    
    mandatoryGroup.add_option("-l", "--logs", action="store", dest="logs", nargs=2, default=None, help="2 paths to logs directory")
   
    optionalGroup.add_option("-d", "--diff", action="store_true", dest="diff", default=False, help="run sh diff.")
    optionalGroup.add_option("-D", "--Diff", action="store_true", dest="Diff", default=False, help="run pithon diff.")
    optionalGroup.add_option("-t", "--strip", action="store_false", dest="strip", default= True, help="Do not run strip on the files")
    optionalGroup.add_option("-b", action="store_false",dest="heartBeet",default=True, help="don't ignore heart beet messages.")
    optionalGroup.add_option("-i", action="store_false",dest="subscribe",default=True, help="don't ignore heart beet and subscribe messages.")
    optionalGroup.add_option("--noRates", action="store_true",dest="no_rates",default=False, help="do not analize rate files.")
    optionalGroup.add_option("--noTrades", action="store_true",dest="no_trades",default=False, help="do not analize trade files.")
    optionalGroup.add_option("-s", "--silent", action="store_true",dest="silent",default=False, help="orint only minimal output.")
    optionalGroup.add_option("-v", "--verbose",action="store_true",dest="verbose",default=False, help="Print full output.")
    
    options.add_option_group(mandatoryGroup)
    options.add_option_group(optionalGroup)
    
    (op,args) = options.parse_args()
    
    if op.logs: #Mandatory field
        if op.verbose: print op.logs
        if not os.path.isdir(op.logs[0]) :
            options.error(color.red('"-l, --logs" first argumet got invalid path'))
        if not os.path.isdir(op.logs[1]):
            options.error(color.red('"-l, --logs" second argumet got invalid path'))
    else:
        options.error(color.red('"-l, --logs" is not defined.\n'))
    if op.verbose and op.silent:
        options.error(color.red('"-s,--silent" and "-v, --verbose" cannot be set together'))
    return (op, args)

# Strip rate log - the rates output from FIXation
def stripRates(fileFullPath,newFileFullpath,silent):
    if os.path.isfile(newFileFullpath):
        if not silent: print newFileFullpath, color.turquoise("already exist")
        return
    if not silent: print color.blue("striping"), fileFullPath, "to", newFileFullpath
    with open(fileFullPath,'r') as src:
        with open(newFileFullpath,'w') as dest:
            for line in src:
                dest.write(','.join(line.split(',')[3:])+'\n')

# strip the FIX logs input to SimFix and to Fixation 
def stripFIX(fileFullPath,newFileFullpath,ignore,silent):
    import re
    if os.path.isfile(newFileFullpath):
        if not silent: print newFileFullpath, color.turquoise("already exist")
        return
    if not silent: print color.blue("striping"), fileFullPath, "to", newFileFullpath
    with open(fileFullPath,'r') as src:
        with open(newFileFullpath,'w') as dest:
            for line in src:
                if line.find(',rcv') == -1:continue
                if ignore and re.search(r'35=[0,1]',line): continue #remove heartbeet
                if ignore == 2 and re.search(r'35=A',line): continue #remove subscribe
                try:
                    line = ' '.join(line.split()[1:])
                    line = re.sub(r'9=[0-9]+','',line)  #remove the message length
                    line = re.sub(r'[0-9]+=[0-9]{8}-[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9]{3,6}','',line)  # remove time-stamp
                    line = re.sub(r'34=[0-9]+','',line)  # remove message counter
                    line = re.sub(r'262=[A-Z][0-9]?','',line)  # remove ccypair subscribe letter
                    line = re.sub(r'10=[0-9]{3}','',line)    # remove checksum
                    dest.write(line + '\n')
                except:
                    print line

def preStrip(path,ignore,silent,no_trades,no_rates):
    for file in os.listdir(path):
        fileFullPath = path + "/" + file
        newFileFullpath = path + "/extracted_logs/" + file
        if len(file.split('_'))<2:continue
        #if file == "extracted_logs": continue
        if file.split('_')[0]=='rates':
            stripRates(fileFullPath,newFileFullpath,silent)
        if not no_rates and file.split('_')[-2] == 'rates': # or file.split('_')[-2] == 'trades':
            stripFIX(fileFullPath,newFileFullpath,ignore,silent)
        if not no_trades and file.split('_')[-2] == 'trades':
            stripFIX(fileFullPath,newFileFullpath,ignore,silent)

def stripLogs(op):
    ignore =  2 if op.subscribe else 1 if op.heartBeet else 0
    preStrip(op.logs[0],ignore,op.silent,op.no_trades,op.no_rates)
    preStrip(op.logs[1],ignore,op.silent,op.no_trades,op.no_rates)

def compareLogs(op):
    import filecmp
    diff = []
    Pass = True
    if not op.silent: print "starting compare!"
    fileList1 = os.listdir(op.logs[0] + "/extracted_logs/")
    fileList2 = os.listdir(op.logs[1] + "/extracted_logs/")
    for file1 in fileList1:
        if not file1.split('.')[-1] == "log": continue
        if op.no_trades and file1.split('_')[-2] == 'trades': continue
        if op.no_rates and file1.split('_')[-2] == 'rates': continue
        #lpFile1 = file1.split('_')
        for file2 in fileList2:
            #lpFile2 = file2.split('_')
            if file1.split('_')[0:-1] == file2.split('_')[0:-1]: # lpFile1[0] == lpFile2[0] and lpFile1[1] == lpFile2[1]:
                print "compareing:", op.logs[0] + "/extracted_logs/" + file1, op.logs[1] + "/extracted_logs/" + file2 + ' - ',
                if op.Diff:
                    if filecmp.cmp(op.logs[0] + "/extracted_logs/" + file1, op.logs[1] + "/extracted_logs/" + file2):
                        print color.green("Pass")
                    else:
                        Pass = False
                        print color.red("Failed") 
                if op.diff:
                    diffCmd = "diff  " + (op.logs[0] + "/extracted_logs/" + file1 + " " + op.logs[1] + "/extracted_logs/" + file2)
                    if op.verbose: print diffCmd + ' - ',
                    a = commands.getoutput(diffCmd)
                    if a == "": 
                        print color.green("Pass")
                    else:
                        Pass = False
                        print color.red("Failed")
                        if op.verbose: print a
                fileList2.remove(file2)

    return Pass

def main(op): # This function will run all basic usage of SimFix_Suit_Infrastructure.
    print color.brown("\n\t*** SimFix - Suit ***\n")

    setAboutValue("logs", op.logs)
    
    mkdirs(op.logs[0] + "/extracted_logs/")
    mkdirs(op.logs[1] + "/extracted_logs/")
    
    if op.strip:
        stripLogs(op)   
    
    if op.diff or op.Diff:
        if compareLogs(op): 
            print color.green("Pass All")
        else:
            if op.silent: print color.red("failed")

if(__name__ == "__main__"):
    try:
        op, args = getOptions(sys.argv)
    except Exception, e:
        print >> sys.stderr, e            
        sys.exit(2)
       
    main(op)
    
    
#test comment 2 erez   
