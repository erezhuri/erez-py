#!/usr/bin/env python
import os, sys
from E_lib import paintText, mkdirs
color = paintText()

def getOptions(argv): # This function will Parse cmdline options
    import optparse
    
    usage = "\t%prog [options] \n\t%prog --help"
    
    options = optparse.OptionParser(usage, version="Rev. 1")
    options.add_option("-l", "--log", action="store", dest="log", default=None, help="log of FIX messages")
    options.add_option("--lp", action="store", dest="lp", default=None, help="comma separated list of lp codes or 'all' to extract from stream client log (leve empty if it is an LP log instead of SC)")
    options.add_option('-d', '--dest', action="store", dest="dest", default='./new/', help='destination of output files (./new/ dir is default)')
    options.add_option("-i", "--ignoreHB",action="store_true",dest="HB",default=True, help="do not try to pars hurtbeet and subscribe.")
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
    
    return (op, args)

def lpNames (fix_msg): 
    for tag in fix_msg:
        tag = tag.split('=')
        if tag[0] == '115' :
            return tag[1]
    return 'noLP'
        
def fixToDict(fix_msg):
    fix_msg_dict = {}
    if op.verbose : print 'fixToDict: ',
    for tag in fix_msg:
        tag = tag.split('=')
        tag[1] = tag[1].translate(None,'/@') if tag[0] in ('55','262') else tag[1]
        tag[1] = tag[1].rjust(15) if tag[0] not in ('35','115') else tag[1]
        if fix_msg_dict.get(tag[0]):
            fix_msg_dict[tag[0]] = fix_msg_dict[tag[0]] + ', ' + tag[1]
            #fix_msg_dict[tag[0]].append(tag[1])
        else:
            if op.verbose : print tag ,
            fix_msg_dict[tag[0]] = tag[1]
            #fix_msg_dict[tag[0]]=[tag[1]]
    if op.verbose : print 
    return fix_msg_dict

def rateExtractFromDict(fix_msg_dict):
    book_update = ''
    if fix_msg_dict['35'] == 'X' or fix_msg_dict['35'] == 'W' :
        book_update = "MsgType   : " + fix_msg_dict['35'] \
        + "\ntimestamp : " + fix_msg_dict['52'] \
        + "\nSymbol    : " + fix_msg_dict.get('55',fix_msg_dict.get('262','None')) \
        + "\nside      : " + fix_msg_dict.get('269','Bad rate!!!!') \
        + "\naction    : " + fix_msg_dict.get('279','None') \
        + "\nentryID   : " + fix_msg_dict.get('278',fix_msg_dict.get('299','None')) \
        + "\nprice     : " + fix_msg_dict.get('270','None') \
        + "\nvolume    : " + fix_msg_dict.get('271','None') \
        +'\n'
        #+ "\nlp " + fix_msg_dict.get('115','None') \
    elif fix_msg_dict['35'] == 'S' or fix_msg_dict['35'] == 'i':
        book_update = "MsgType   : " + fix_msg_dict['35'] \
        + "\ntimestamp : " + fix_msg_dict['52'] \
        + "\nSymbol    : " + fix_msg_dict.get('55','None') \
        + "\nbid price : " + fix_msg_dict['132'] \
        + "\nbid volume: " + fix_msg_dict['134'] \
        + "\nask price : " + fix_msg_dict['133'] \
        + "\nask volume: " + fix_msg_dict['135'] \
        +'\n'
        #+ "\nlp " + fix_msg_dict.get('115') \
    return fix_msg_dict.get('115'),book_update       
        

 
def prepareLine(line):
    if op.verbose : print '\nprepareLine: ' + line
    if line.find("rcv") == -1 and line.find("snd") == -1 : return None ,None
    if line[-1] == '\n' : line = line[:-1]
    if line[-1] == '\r' : line = line[:-1]
    if line[-1] == '' : line = line[:-1]
    splitedLine = line.split(" ")
    i = 0
    fullMsg = ''
    for elm in splitedLine :
        if elm[0] == '8' : 
            fullMsg = " ".join(splitedLine[i:])
            break
        i += 1
    fix_msg = fullMsg.split('')
    if op.verbose : print 'log-time: ' + splitedLine[0] + 'prepareLine: ' + ' | '.join(fix_msg)
    if fix_msg [2][1] == '35' and (fix_msg [2][1] == '0' or fix_msg [2][1] == '1' or fix_msg [2][1] == 'V') and op.HB : return splitedLine[0], None
    return '-------------log-time: ' + splitedLine[0] + '\n', fix_msg

def main(op):
    logName = os.path.split(op.log)[1]
    logName = logName.split(".")[0]
    #outputFile = op.dest + logName + ( '_' + op.lp if op.lp else '') + '_book_pars.log'
    outFiles = {}        
    if op.lp != 'all':
        if op.lp :
            op.lp = op.lp.split(',')
        else:
            op.lp = ['']
        for lp in op.lp:
            outputFile = op.dest + logName + '_' + lp + '_book_pars.log'
            outFiles[lp] = open(outputFile, 'w')
    with open(op.log,"r") as logF :
        for line in logF:
            logTime, fix_msg = prepareLine(line)
            if fix_msg:
                fix_msg_dict = fixToDict(fix_msg)
            
                LP,book_update = rateExtractFromDict(fix_msg_dict)
                if op.verbose : print LP,book_update
                if LP == None and op.lp == [''] : LP = ''
                if book_update :
                    if op.lp == 'all' or LP in op.lp :
                        if outFiles.get(LP):
                            outFiles[LP].writelines(logTime)
                            outFiles[LP].writelines(book_update)
                        else:
                            outputFile = op.dest + logName + '_' + LP + '_book_pars.log'
                            outFiles[LP] = open(outputFile, 'w')
                            outFiles[LP].writelines(logTime)
                            outFiles[LP].writelines(book_update)
    for LP in outFiles:
        outFiles[LP].close()
 
if(__name__ == "__main__"):
    try:
        op, args = getOptions(sys.argv)
    except Exception, e:
        print >> sys.stderr, e            
        sys.exit(2)
       
    main(op)



