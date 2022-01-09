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
    
    mandatoryGroup.add_option("-l", "--logs", action="store", dest="logs", default=None, help="path to logs")
    optionalGroup.add_option("-v", "--verbose",action="store_true",dest="verbose",default=False, help="Print full output.")
    
    options.add_option_group(mandatoryGroup)
    options.add_option_group(optionalGroup)
    
    (op,args) = options.parse_args()
    
    if op.logs: #Mandatory field
        if op.verbose: print op.logs
        if not os.path.isdir(op.logs):
            if not os.path.isfile(op.logs):
                options.error(color.red('"-l, --logs" first argumet got invalid path'))
        #if not os.path.isdir(op.logs[1]):
         #   options.error(color.red('"-l, --logs" second argumet got invalid path'))
    else:
        options.error(color.red('"-l, --logs" is not defined.\n'))
    
    return (op, args)


def removeHB(fileFullPath,newFileFullpath,verbose):
    import re
    if os.path.isfile(newFileFullpath):
        print newFileFullpath, color.turquoise("already exist")
        return
    if verbose: print "striping", fileFullPath, "to", newFileFullpath
    with open(fileFullPath,'r') as src:
        with open(newFileFullpath,'w') as dest:
            for line in src:
                #if line.find(',rcv') == -1:continue
                if not re.search(r'35=[0,1]',line):  #remove heartbeet
                    dest.write(line)
                #if ignore == 2 and re.search(r'35=A',line): continue #remove subscribe

def preRemoveFile(path,verbose):
    newFilePath = path.replace('.log','_new.log')
    removeHB(path,newFilePath,verbose)

def preRemoveDir(path,verbose):
    for file in os.listdir(path):
        if file == "new": continue
        if file.find('_') == -1: continue
        if file.split('_')[0] == 'rates':continue
        if file.split('_')[1] == 'rates' or file.split('_')[1] == 'trades':
            fileFullPath = path + "/" + file
            newFileFullpath = path + "/new/" + file
            removeHB(fileFullPath,newFileFullpath,verbose)

def main(op): # This function will run all basic usage of SimFix_Suit_Infrastructure.
    print color.brown("\n\n\t*** SimFix - remove hartbit ***\n")
    #setAboutValue("logs", op.logs)
    if os.path.isdir(op.logs):
        mkdirs(op.logs + "/new/")
        preRemoveDir(op.logs,op.verbose)
    else:
        preRemoveFile(op.logs,op.verbose)

if(__name__ == "__main__"):
    try:
        op, args = getOptions(sys.argv)
    except Exception, e:
        print >> sys.stderr, e            
        sys.exit(2)
       
    main(op)
