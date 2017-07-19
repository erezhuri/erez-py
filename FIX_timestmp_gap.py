#!/usr/bin/env python
import os, sys, datetime, time
from E_lib import paintText, mkdirs
import traceback
color = paintText()

previusLineTime = {'sendingTime':None, 'origSendingTime':None, 'lastUpdateTime':None, 'ccy':None}
currentLineTime = {'sendingTime':None, 'origSendingTime':None, 'lastUpdateTime':None, 'ccy':None}
elapsedTimeList=[]
sendingTimeDeltaList=[]
lastUpdateTimeDeltaList=[]
origSendingTimeDeltaList=[]
lastUpdateTimeDeltaPerCCY={}

def getOptions(argv): # This function will Parse cmdline options
    import optparse
    
    usage = "\t%prog [options] \n\t%prog --help"
    
    options = optparse.OptionParser(usage, version="Rev. 1")
    options.add_option("-l", "--log", action="store", dest="log", default=None, help="log of FIX messages")
    options.add_option("-L", "--logList", action="store", dest="logList", default=None, help="List of logs")
    options.add_option('-d', '--dest', action="store", dest="dest", default='./new/', help='destination of output files (./new/ dir is default)')
    options.add_option("-i", "--ignoreHB",action="store_true",dest="HB",default=True, help="do not try to pars hurtbeet and subscribe.")
    options.add_option("-s", "--summarry",action="store_true",dest="summarry",default=False, help="Write only summarry to output file.")
    options.add_option("-p", "--percentile",action="store",dest="percentile",default="90,99,99.9,100", help="list of percentile to calculate. (default - 90,99,99.9,100)")
    options.add_option("-n", "--ignoreRates",action="store",dest="ignoreRates",default=0, type=int, help="How meny rates to ignore before start clculation (default - 0).")
    options.add_option("-v", "--verbose",action="store_true",dest="verbose",default=False, help="Print full output.")
    op, args = options.parse_args()
    #--------------------------------------------
    if op.log:
        if op.logList:
            raise options.error(color.red('"-l, --log" and "-L,--logList" are defined. only one of them should be defined \n'))     
        if not os.path.isfile(op.log):
            options.error(color.red('"-l, --log" got invalid path'))
    elif op.logList:
        op.logList = op.logList.split()
        op.logList = op.logList + args
        for l in op.logList:
            if not os.path.isfile(l):
                options.error(color.red('one of the logs in the list have invalid path\n'))
    else:
        raise options.error(color.red('"-l, --log" and "-L,--logList" is not defined. one of them should be defined \n'))     
        
    if op.dest == './new/':
        mkdirs(op.dest)
    else:
        if not os.path.isdir(op.dest):
            options.error(color.red('"-d, --dest" got invalid path'))
    
    return (op, args)

def prepareLine(line):
    if op.verbose : print '\nprepareLine: ' + line
    if line.find("rcv") == -1 and line.find("snd") == -1 : return None ,None, None
    if line[-1] == '\n' : line = line[:-1]
    if line[-1] == '\r' : line = line[:-1]
    if line[-1] == '' : line = line[:-1]
    splitedLine = line.split(" ")
    logTime = splitedLine[0]
    
    i = 0
    fullMsg = ''
    logDirection = ''
    for elm in splitedLine :
        if elm[0] == '8' : 
            fullMsg = " ".join(splitedLine[i:])
            break
        if elm[0] == 'snd,' or elm[0] == 'rcv,':
            logDirection = elm[0][:-1]
        i += 1
    fix_msg = fullMsg.split('')
    if op.verbose : print 'log-time: ' + splitedLine[0] + 'prepareLine: ' + ' | '.join(fix_msg)
    if fix_msg [2][1] == '35' and (fix_msg [2][1] == '0' or fix_msg [2][1] == '1' or fix_msg [2][1] == 'V') and op.HB : return splitedLine[0], None, None
    return splitedLine[0], logDirection, fix_msg

def timestampExtractFromFix(fix_msg):
    global currentLineTime
    SendingTime = OrigSendingTime = LastUpdateTime = None
    for tag in fix_msg:
        tag = tag.split('=')
        if tag[0] == '97': return None, None, None
        if tag[0] == '35' and tag[1] != 'W' : return None, None, None
        if tag[0] == '269' and tag[1] == 'J' : return None, None, None
#         if tag[0] == '262': ccy = tag[1].translate(None,'/@')
        if tag[0] == '55': ccy = tag[1].translate(None,'/@')
        if tag[0] == '52': SendingTime = tag[1]
        if tag[0] == '122': OrigSendingTime = tag[1]
        if tag[0] == '779': LastUpdateTime = tag[1]
    if op.verbose : print "timestampExtractFromFix" + SendingTime +','+ OrigSendingTime +','+ LastUpdateTime
    if lastUpdateTimeDeltaPerCCY.get(ccy):
        lastUpdateTimeDeltaPerCCY[ccy].append([0,LastUpdateTime]) 
    else:
        lastUpdateTimeDeltaPerCCY[ccy] = [[0,LastUpdateTime]]
  
    #currentLineTime = {'sendingTime':SendingTime, 'origSendingTime':OrigSendingTime, 'lastUpdateTime':LastUpdateTime, 'ccy':ccy}
    return 

def strDiffIndex (a, b):
    lenA =  len(a)
    lenB =  len(b)
    lenC = max(lenA,lenB)
    try:
       return [i for i in  range(lenC) if i >= lenB or i >= lenA or a[i] != b[i]]
    except:
       return [i for i in xrange(lenC) if i >= lenB or i >= lenA or a[i] != b[i]] 

def timeDelta(t1,t2):
    index = strDiffIndex(t1,t2)
    if index == []: return 0
    if index[0] < 8:
        try:
            delta = datetime.datetime.strptime(t1, "%Y%m%d-%H:%M:%S.%f") - datetime.datetime.strptime(t2, "%Y%m%d-%H:%M:%S.%f")
            return delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10**6
        except:
            print "Error - Faild to calculate date"
            return -999999
    
    microT1 = int(t1[18:])
    microT2 = int(t2[18:])
    if index[0] > 17:
        return microT1 - microT2
    secondsT1 = int(t1[15:17])
    secondsT2 = int(t2[15:17])
    if index[0] > 14:
        return (secondsT1*1000000 + microT1) - (secondsT2*1000000 + microT2)
    minuetT1 = int(t1[12:14])
    minuetT2 = int(t2[12:14])
    if index[0] > 11:
        return ((minuetT1*60 + secondsT1)*1000000 + microT1) - ((minuetT2*60 + secondsT2)*1000000 + microT2)
    hourT1 = int(t1[9:11])
    hourT2 = int(t2[9:11])
    if index[0] > 8:
        return (((hourT1*60 + minuetT1)*60 + secondsT1)*1000000 + microT1) - (((hourT2*60 + minuetT2)*60 + secondsT2)*1000000 + microT2)

def latecyCalc(fix_msg):
    global currentLineTime,previusLineTime,sendingTimeDeltaList,lastUpdateTimeDeltaList,origSendingTimeDeltaList
    
    
    if not currentLineTime['sendingTime'] or not currentLineTime['lastUpdateTime'] or not currentLineTime['origSendingTime']: 
       #print currentLineTime,currentLineTime,currentLineTime
       return

    
    sendingTimeDelta = timeDelta(currentLineTime['sendingTime'],previusLineTime['sendingTime']) if previusLineTime['sendingTime'] else '---'
    lastUpdateTimeDelta = timeDelta(currentLineTime['lastUpdateTime'],previusLineTime['lastUpdateTime']) if previusLineTime['lastUpdateTime'] else '---'
    origSendingTimeDelta = timeDelta(currentLineTime['origSendingTime'],previusLineTime['origSendingTime']) if previusLineTime['origSendingTime'] else '---'
    
    
    if op.verbose : print "time:" , currentLineTime['sendingTime'], currentLineTime['lastUpdateTime'], currentLineTime['origSendingTime']
    #if lastUpdateTimeDelta != '---':
    sendingTimeDeltaList.append((sendingTimeDelta, currentLineTime['lastUpdateTime']))
    lastUpdateTimeDeltaList.append((lastUpdateTimeDelta, currentLineTime['lastUpdateTime']))
    origSendingTimeDeltaList.append((origSendingTimeDelta, currentLineTime['lastUpdateTime']))
    #print sendingTimeDelta, lastUpdateTimeDelta, origSendingTimeDelta, currentLineTime['sendingTime']
    previusLineTime = currentLineTime
    return 


def main(op):
    global  currentLineTime,previusLineTime,sendingTimeDeltaList,lastUpdateTimeDeltaList,origSendingTimeDeltaList
    try:
        startTime = time.time()
        logName = os.path.split(op.log)[1]
        logName = logName.split(".")[0]
        outputFile = op.dest + logName + '_TimeStamp_gap.log'
        print "=== Analyzing log:",logName,'==='
        with open(op.log,"r") as logF :
            for line in logF:
                logTime, logDirection, fix_msg = prepareLine(line)
                #print '\r',logTime,
                if fix_msg:
                    timestampExtractFromFix(fix_msg)
        latecyCalc(fix_msg) 
        print    
        for key in lastUpdateTimeDeltaPerCCY:
            lastUpdateTimeDeltaPerCCY[key].sort(key=lambda x:x[1])
            length = len(lastUpdateTimeDeltaPerCCY[key])
            for i in range(1,length):
                lastUpdateTimeDeltaPerCCY[key][i][0] = timeDelta(lastUpdateTimeDeltaPerCCY[key][i][1],lastUpdateTimeDeltaPerCCY[key][i-1][1])
            lastUpdateTimeDeltaPerCCY[key].sort(key=lambda x:x[0])
            lastUpdateTimeDeltaPerCCY[key] = lastUpdateTimeDeltaPerCCY[key][length//4:]
#         origSendingTimeDeltaList.sort()
#         lastUpdateTimeDeltaList.sort()
#         sendingTimeDeltaList.sort()
        with open(outputFile, 'w') as outFile:
            outFile.writelines('origSendingTimeDelta,lastUpdateTime|lastUpdateTimeDelta,lastUpdateTime|sendingTimeDelta,lastUpdateTime\n')
            for key in lastUpdateTimeDeltaPerCCY:
                outFile.writelines("==="+key+"===\n")
                for i in lastUpdateTimeDeltaPerCCY[key]:
#                     print key,i 
                    outFile.writelines(key + str(i)+'\n')
                #outFile.writelines(str(x[0][0])+','+str(x[0][1])+'|'+str(x[1][0])+','+str(x[1][1])+'|'+str(x[2][0])+','+str(x[2][1])+'\n')
#             outFile.writelines(logTime.ljust(26) + ',' + outLine)
#             elapsedTimeList = elapsedTimeList[op.ignoreRates:]
#             median, minLatency =  getMedianAndMin()
#             outFile.writelines("min latency " + str(minLatency) + ' micro-sec\n')
#             print "min latency:", minLatency,'micro-sec.'
#             outFile.writelines("Median: " + str(median) + ' micro-sec\n')
#             print "Median latency: " , median,'micro-sec.'
#             pecenteList = op.percentile.split(',')  #[10,20,30,40,50,60,70,80,90,99,99.9,99.99,99.999,100]
#             for pcnt in pecenteList:
#                 avg, count, maxLatency, outputString = percentAvg(pcnt)
#                 #outFile.writelines("Average latency of " + pcnt + "%: " + str(avg) + ' micro-sec from ' + str(count) + ' rates. Max ' + pcnt + '% latecy: ' + str(maxLatency) + ' micro-sec\n')
#                 print outputString
#                 outFile.writelines(outputString + '\n')
        endTime = time.time()
        print 'Total run for log:',logName,'is:', endTime - startTime, 'sec.'
    except Exception, e:
        endTime = time.time()
        print 'Total run for log:',logName,'is:', endTime - startTime, 'sec.'
        print(traceback.format_exc())
        sys.exit(2)
        
if(__name__ == "__main__"):
    
    try:
        op, args = getOptions(sys.argv)
    except Exception, e:
        print >> sys.stderr, e            
        sys.exit(2)
    if op.logList:
#         ignoreCount = op.ignoreRates
        for l in op.logList:
            op.log = l
            main(op)
#             op.ignoreRates = ignoreCount 
    else:
        main(op)

        

