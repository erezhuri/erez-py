#!/usr/bin/env python
import os, sys, datetime, time
from E_lib import paintText, mkdirs
import traceback
color = paintText()

maxElapsedTime=0
sumElapsedTime=0
elapsedTimeList=[]

def getOptions(argv): # This function will Parse cmdline options
    import optparse
    
    usage = "\t%prog [options] \n\t%prog --help"
    
    options = optparse.OptionParser(usage, version="Rev. 1")
    options.add_option("-l", "--log", action="store", dest="log", default=None, help="log of FIX messages")
    options.add_option("-L", "--logList", action="store", dest="logList", default=None, help="List of logs")
    options.add_option('-d', '--dest', action="store", dest="dest", default='./new/', help='destination of output files (./new/ dir is default)')
    options.add_option("-H", "--ignoreHB",action="store_true",dest="HB",default=True, help="do not try to pars hurtbeet and subscribe.")
    options.add_option("-s", "--summarry",action="store_true",dest="summarry",default=False, help="Write only summarry to output file.")
    options.add_option("-w", "--network",action="store_true",dest="network",default=False, help="Calc network transfer time.")
    options.add_option("-t", "--total",action="store_true",dest="total",default=False, help="Calc total network transfer + internal processing time.")
    options.add_option("-i", "--internal",action="store_true",dest="internal",default=False, help="Calc internal processing time.")
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
            
    if not (op.network or op.total or op.internal):
        op.internal = True
    
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
    SendingTime = OrigSendingTime = LastUpdateTime = None
    for tag in fix_msg:
        tag = tag.split('=')
        if tag[0] == '97': return None, None, None
        if tag[0] == '35' and tag[1] != 'W' : return None, None, None
        if tag[0] == '269' and tag[1] == 'J' : return None, None, None
        #if tag[0] == '269' and tag[1] == '2' : 
#         if op.ignoreRates > 0 :
#             op.ignoreRates -= 1
#             print op.ignoreRates
#             return None, None, None
        if tag[0] == '52': SendingTime = tag[1]
        if tag[0] == '122': OrigSendingTime = tag[1]
        if tag[0] == '779': LastUpdateTime = tag[1]
    if op.verbose : print "timestampExtractFromFix" + SendingTime +','+ OrigSendingTime +','+ LastUpdateTime
    return SendingTime, OrigSendingTime, LastUpdateTime

def strDiffIndex (a, b):
    lenA =  len(a)
    lenB =  len(b)
    lenC = max(lenA,lenB)
    try:
       return [i for i in  range(lenC) if i >= lenB or i >= lenA or a[i] != b[i]]
    except:
       return [i for i in xrange(lenC) if i >= lenB or i >= lenA or a[i] != b[i]] 

def timeDelta(t1,t2):
    #t1 = t1 + '000' if len(t1) == 21 else t1
    #t2 = t2 + '000' if len(t1) == 21 else t2
    index = strDiffIndex(t1,t2)
    #print 'Debug -', index
    if len(index) == 0: return 0
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
    global maxElapsedTime, sumElapsedTime, elapsedTimeList
    
    sendingTime, origSendingTime, lastUpdateTime = timestampExtractFromFix(fix_msg)
    if not sendingTime or not lastUpdateTime or not origSendingTime: return 
    returnStr = origSendingTime.ljust(35) + ',' + sendingTime.ljust(35) + ',' + lastUpdateTime.ljust(35)
    if op.internal: 
        elapsedTime = timeDelta(sendingTime, lastUpdateTime) * 1.0 if lastUpdateTime else '---'
        if elapsedTime != '---':
            elapsedTimeList.append( elapsedTime )
        returnStr += ',' + str(elapsedTime).ljust(35)
    if op.network: 
        networkTime = timeDelta(lastUpdateTime, origSendingTime) * 1.0 if lastUpdateTime and origSendingTime else '---'
        returnStr += ',' + str(networkTime).ljust(35)
    if op.total: 
        elapsedTimeExt = timeDelta(sendingTime, origSendingTime) * 1.0 if origSendingTime else '---'
        returnStr += ',' + str(elapsedTimeExt).ljust(35)
    if op.verbose : 
        print "time:" , sendingTime, origSendingTime, lastUpdateTime, elapsedTime
    returnStr += '\n'
    return returnStr


def getMedianAndMin():
    global elapsedTimeList
    elapsedTimeList.sort()
    listLen = len(elapsedTimeList)
    index = listLen // 2
    if listLen <= 0: return 0,0
    return (elapsedTimeList[index] if listLen % 2 else (elapsedTimeList[index] + elapsedTimeList[index + 1])/ 2.0), elapsedTimeList[0] 


def percentAvg(percent):
    global elapsedTimeList
    index = int((len(elapsedTimeList)-1) * float(percent) / 100)
    if index <= 0 : 
        #print    "Avarage latency of",   percent + '% is: 0 micro-sec from 0 rates. Max latency of',   percent + '% is: 0 micro-sec.'
        outStr = 'Average latency of ' + percent.rjust(6) + '% is: 0 micro-sec from 0 rates. Max latency of ' + percent.rjust(6) + '% is: 0 micro-sec'
        return 0,0,0,outStr
    elapsedTimeList.sort()
    pcntAvg = sum(elapsedTimeList[:index])/(index+1.0)
    #print    "Average latency of",   percent + '% is:',pcntAvg         ,  'micro-sec from', index+1,          'rates. Max latency of',percent +    '% is:',   elapsedTimeList[index],'micro-sec.'
    outStr = 'Average latency of ' + percent.rjust(6) + '% is: ' + str(pcntAvg).rjust(16) + ' micro-sec from ' + str(index+1) + ' rates. Max latency of ' + percent.rjust(6) + '% is: ' + str(elapsedTimeList[index]) + ' micro-sec'
    return pcntAvg, index+1, elapsedTimeList[index], outStr

def main(op, initialOutLine):
    global elapsedTimeList
    try:
        startTime = time.time()
        logName = os.path.split(op.log)[1]
        logName = logName.split(".")[0]
        outputFile = op.dest + logName + '_LatencyCalc' + ('Internal' if op.internal else '') + ('Network' if op.network else '') + ('Total' if op.total else '') + '.csv'
        print "=== Analyzing log:",logName,'==='
        global maxElapsedTime, sumElapsedTime
        with open(outputFile, 'w') as outFile:
            with open(op.log,"r") as logF :
                if not op.summarry: outFile.writelines(initialOutLine)
                for line in logF:
                    logTime, logDirection, fix_msg = prepareLine(line)
                    if fix_msg:
                        outLine = latecyCalc(fix_msg) 
                        if outLine and not op.summarry: 
                            outFile.writelines(logTime.ljust(35) + ',' + outLine)
            elapsedTimeList = elapsedTimeList[op.ignoreRates:]
            median, minLatency =  getMedianAndMin()
            outFile.writelines("min latency " + str(minLatency) + ' micro-sec\n')
            print "min latency:", minLatency,'micro-sec.'
            outFile.writelines("Median: " + str(median) + ' micro-sec\n')
            print "Median latency: " , median,'micro-sec.'
            pecenteList = op.percentile.split(',')  #[10,20,30,40,50,60,70,80,90,99,99.9,99.99,99.999,100]
            for pcnt in pecenteList:
                avg, count, maxLatency, outputString = percentAvg(pcnt)
                #outFile.writelines("Average latency of " + pcnt + "%: " + str(avg) + ' micro-sec from ' + str(count) + ' rates. Max ' + pcnt + '% latecy: ' + str(maxLatency) + ' micro-sec\n')
                print outputString
                outFile.writelines(outputString + '\n')
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
    initialOutLine = "Log Time".ljust(35) + ", Original Sending Time(122)".ljust(35) + ", Sending Time(52)".ljust(35) + ", Last Update Time(779)".ljust(35)
    if op.internal: initialOutLine += ", Elapsed Time (52 - 779)".ljust(35) 
    if op.network: initialOutLine +=  ", network Transfer Time (779-122)".ljust(35)
    if op.total: initialOutLine +=    ", External Elapsed Time (122-52)".ljust(35) 
    initialOutLine += "\n"
    if op.logList:
#         ignoreCount = op.ignoreRates
        for l in op.logList:
            op.log = l
            main(op, initialOutLine)
#             op.ignoreRates = ignoreCount 
    else:
        main(op, initialOutLine)

        
