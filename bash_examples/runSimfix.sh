#!/bin/sh


usage()
{
cat << EOF
usage: $0 options

This script run FIXation/FTT with SimFix

OPTIONS:
   -h      Show this message
   -l      List if logs to run
   -c      cfg file
   -n      connectivity.cfg file
   -i      licence
   -s      SimFix executable file (file name mast contain one of the words "ftt/fixation")
   -f      FIXation/ftt executable file
   -o      output location
   -t      enter the timeout in seconds (default: 50400)
   -b      HB seconds (default: 28000)
   -S      set stress run 
   -m      multiprocess -> staret FIXation first (do not work wuth -t)
   -v      Verbose

EOF
#turn this on if you run Ftt Binary (do not work wuth -m)
}



setup()
{
	mkdir -p $OUTPUT_DIR
	cd $OUTPUT_DIR
	cp $LIST $OUTPUT_DIR/log.list
	if [[ $FTT_BINARY ]]
	then
		sed -e "s:log_path=.*:log_path=$OUTPUT_DIR:" -e "s:startup_actions=2:startup_actions=0:" $CFG > $OUTPUT_DIR/app.cfg
		sed -e "/startup_actions=*/d" $CONNECTIVITY > $OUTPUT_DIR/connectivity.cfg
      cp $LIC $OUTPUT_DIR/risk.lic
	else
		sed "s:log_path=.*:log_path=$OUTPUT_DIR:" $CFG > $OUTPUT_DIR/app.cfg
		cp $CONNECTIVITY $OUTPUT_DIR/connectivity.cfg
      cp $LIC $OUTPUT_DIR/risk.lic
	fi

	if [ $1 ]
	then
		if [[ -z $TERM ]];then echo " ** Input parameters **  "
		fi
		echo "SimFix: $SIMFIX"
		fh_str=$([ "$FTT_BINARY" ] && echo "Ftt" || echo "FIXation")
		echo "$fh_str: $BINARY"
		echo "config files:"
		echo "LIST: $LIST"
		echo "CFG: $CFG"
		echo "CONNECTIVITY: $CONNECTIVITY"
		echo "copied to:" 
		echo "OUTPUT_DIR: $OUTPUT_DIR"
		echo "RUN_TIME: $RUN_TIME"
		echo "exra parameters:"
		echo "MULTIPROCESS: $MULTIPROCESS"
		echo "HBtime: $HBtime"
		echo "time: $time"
	fi
}

Run_SimFix()
{

#   echo "   === RUNNING SIMFIX ==="

	if [[ $SIMFIX == *stable* ]]
	then
#		echo "no log (-f)"
		timeout $time $SIMFIX -n -s 0  -p $HBtime $OUTPUT_DIR/log.list > $OUTPUT_DIR/SimFix_screen.log 2>&1&
	else
		if [[ $SIMFIX == *mp* ]] || [[ $SIMFIX == *sp* ]]
		then
			timeout $time $SIMFIX -n  -s 51  -p $OUTPUT_DIR/log.list > $OUTPUT_DIR/SimFix_screen.log 2>&1&
      else
			#     echo "with log (-f)"
      timeout $time $SIMFIX -f $OUTPUT_DIR/SimFix.log -n -s 50 -p  $OUTPUT_DIR/log.list > $OUTPUT_DIR/SimFix_screen.log 2>&1&
	fi
	fi


   echo "=== Start SimFix at: `date +%D_%T:%N`"
        START_SIMFIX=$(date +%s)

	PIDOF_SIMFIX_TIMER=$!
	PIDOF_SIMFIX=`ps -ef|grep $PIDOF_SIMFIX_TIMER|egrep -v "grep|timeout"|gawk '{print $2}'`
	sleep 20
	if [[ $VERBOSE ]]
	then
		echo $PIDOF_SIMFIX
		echo `ps -ef|grep $PIDOF_SIMFIX|grep -v grep`
	fi
}



Run_Ftt()
{
#   echo "   === RUNNING FTT ==="
	
#	$BINARY -v
	timeout $time $BINARY -cfg $OUTPUT_DIR/app.cfg -cfg $OUTPUT_DIR/connectivity.cfg -cfg $OUTPUT_DIR/risk.lic > $OUTPUT_DIR/Ftt_screen.log 2>&1&
	#$BINARY -cfg $OUTPUT_DIR/app.cfg -cfg $OUTPUT_DIR/connectivity.cfg > $OUTPUT_DIR/Ftt_screen.log 2>&1&
	echo "=== Start FTT at: `date +%D_%T:%N`"

	PIDOF_BINARY_TIMER=$!
	PIDOF_BINARY=`ps -ef|grep $PIDOF_BINARY_TIMER|egrep -v "grep|timeout"|gawk '{print $2}'`
	echo "PID: "$PIDOF_BINARY
	if [[ $VERBOSE ]]
	then
		echo $PIDOF_BINARY
		echo `ps -ef|grep $PIDOF_BINARY|grep -v grep`
	fi
	sleep 30
	
   echo "=== move Algo to Test==="
	
	/var/continuousIntegration/run/starter.v2 -test -$REGION -qa
}


Run_FIXation()
{
	
	
#	$BINARY -v
	timeout $time $BINARY $OUTPUT_DIR/app.cfg $OUTPUT_DIR/connectivity.cfg $OUTPUT_DIR/risk.lic > $OUTPUT_DIR/FIXation_screen.log 2>&1&
	echo "=== Start FIXation at: `date +%D_%T:%N`"
        START_FIXATION=$(date +%s)
	
	#PIDOF_FIXation=$!
	PIDOF_BINARY_TIMER=$!
        PIDOF_BINARY=`ps -ef|grep $PIDOF_BINARY_TIMER|egrep -v "grep|timeout"|gawk '{print $2}'`
		  echo "PID: "$PIDOF_BINARY	
        if [[ $VERBOSE ]]
        then
                echo $PIDOF_BINARY
                echo `ps -ef|grep $PIDOF_BINARY|grep -v grep`
        fi
	sleep 30
        #Login_N_Connect
}

Login_N_Connect()
{
	CCY_LIST="EURJPY EURGBP EURCHF USDCHF AUDCHF AUDJPY EURUSD USDJPY GBPUSD USDCAD AUDCAD AUDNZD AUDUSD"
	#LPs=`(echo "clear"; echo "fs"; sleep 1;) | telnet localhost 60009 | egrep -v "^[a-z]|^[A-Z]|>" |awk '{ print $1 }'`
	#alllps=`cat /tmp/remtest_status|egrep -v "^[a-z]|^[A-Z]|>" |awk ' { print $1 }'`
	(
	echo "$CCY_LIST ebsai login"
	#echo "$CCY_LIST $LPs login"
	sleep 20
	echo "subscribe"
	sleep 25
	echo "fs"
	) | telnet localhost 60000
}

Verify()
{
	#FIX_ERROR=`egrep -m 1 "segfault|coredump" $OUTPUT_DIR/Ftt_screen.log`
	#echo $FIX_ERROR
	#if [[ ! -z $FIX_ERROR ]]
	#then

		#echo $FIX_ERROR
		#echo "NOT OK - error/core  - see Ftt_screen.log"
		#exit 2
	#fi
   echo "======================"	
   echo "===Rates validation==="
   echo "======================"
	RATE_COUNT=0	
	#for i in `ls $OUTPUT_DIR/*_rate*`
   for i in `ls ./*_rate*`
	do
		LP_RATES=`grep "rcv" $i | grep -v "^A35=[0,1,V,b,A]" | wc -l`
		LP=`echo $i|cut -f1 -d_`
		echo $LP":" $LP_RATES "rate rows"
		RATE_COUNT=$[ $RATE_COUNT + $LP_RATES ]
	done
	echo "total rates from FIX lpgs: " $RATE_COUNT
	
   FN=`ls $OUTPUT_DIR/rates*`
   echo "FN= " $FN
   if [[  -f $FN ]]
	then
		RN=`cat $FN | wc -l`
		echo "Rates file was created and contains "$RN " lines"
                MixedPrice
   else
      echo "Rates file was not created." 
   fi
   echo "======================="
   echo "===Syslog validation==="
   echo "=======================" 
   if [[  -f $OUTPUT_DIR/current_syslog ]]
	then
      cat $OUTPUT_DIR/current_syslog | grep TIMEOUT
      cat $OUTPUT_DIR/current_syslog | grep fault
      cat $OUTPUT_DIR/current_syslog | egrep -i "error|fail" | egrep -v "timestamp|POOL"
      ppn=`cat $OUTPUT_DIR/current_syslog | egrep -i "POOL PRODUCE returning NULL" | head -1`
             if  [[ ! -z $ppn ]]
             then
                 cat $OUTPUT_DIR/current_syslog | egrep -i "POOL PRODUCE returning NULL" | head -5
                 echo "..........................................."
                 echo "Your sanity failed due to POOL PRODUCE NULL"
                 echo SANITY_FINAL_RESULT 2
                 exit 2
             fi

      drained=`cat $OUTPUT_DIR/current_syslog | egrep -i "drained" | head -1`
             if  [[ ! -z $drained ]]
             then
                 cat $OUTPUT_DIR/current_syslog | egrep -i "drained" | head -5
                 echo "..........................................."
                 echo "Your sanity failed due to drained queue"
                 echo SANITY_FINAL_RESULT 2
                 exit 2
             fi

      died=`cat $OUTPUT_DIR/current_syslog | egrep -i "died" | head -1`
             if  [[ ! -z $died ]]
             then
                 cat $OUTPUT_DIR/current_syslog | egrep -i "died" | head -5
                 echo "..........................................."
                 echo "Your sanity failed due to thread died"
                 echo SANITY_FINAL_RESULT 2
                 exit 2
             fi


   else
      echo "no syslog info found"
	fi
      
}
/*
MixedPrice()
{
CCYLIST="EURUSD EURJPY EURGBP EURCAD USDJPY"
RatesLog=`ls $OUTPUT_DIR/rates*`
flag=0
for f in ./*_rates_*.log
do
        LPName="LP_"`echo $f | cut -d "/" -f2 |cut -d'_' -f1 | tr a-z A-Z`
        echo -e "\n====="$LPName"===== "
        for i in $CCYLIST
             do
                 cat $RatesLog | grep $LPName | grep $i > tmp
                 if [ -s tmp ]; then
                     min=`cat tmp | awk  '{avar=$0;print $3}'| awk  'BEGIN { FS = "," } ;{print $4,$7}'|  grep --only-matching '[[:digit:]]\+' | sort -u | head -1`
                     max=`cat tmp | awk  '{avar=$0;print $3}'| awk  'BEGIN { FS = "," } ;{print $4,$7}'|  grep --only-matching '[[:digit:]]\+' | sort -u | tail -1`
                     if [ "$min"  == "" ]; then
                             echo -ne $i "no data, ";
                     else
                         let "d=$min*100/$max";
                         echo -ne $i $min $max $d " "
                         #echo $d;
                         if [ "$d" -lt "95" ]; then
                              flag=1
                              echo " mixed prices found ";
                              cat tmp |  grep -w $min
                              echo "------"
                              cat tmp  | grep -w $max
                         else
                              echo -ne "no mixed prices, "
                         fi
                    fi
                 else
                     echo -ne $i "- no mixed prices, "
                     rm -f tmp
                 fi
             done
done
echo "flag=" $flag
if [ $flag == 1 ]; then
   #echo "output dir: " $OUTPUT_DIR
   echo "Subject: Mixed price found on FIXation-Trunk-Sanity job" > mail.txt
   echo "" >> mail.txt
   echo "Please check:" >> mail.txt
   echo "Job name: " >> mail.txt;echo  $OUTPUT_DIR | awk -F '[/:]' '{print $5}' >> mail.txt
   echo "Job number:" >> mail.txt; echo  $OUTPUT_DIR | awk -F '[/:]' '{print $6}' >> mail.txt
   #echo "Running time: ">> mail.txt; echo  $OUTPUT_DIR | awk -F '[/:]' '{print $7}' >> mail.txt
   /usr/sbin/sendmail irena@tradigo.co.il noam@tradigo.co.il guy.shimron@tradigo.co.il eh@tradigo.co.il yosi@tradigo.co.il emmanuel@tradigo.co.il <  mail.txt
fi

}
*/

MixedPrice()                        
{
	cd $OUTPUT_DIR
        for f in ./*_rates_*.log
        do
        	LPName="LP_"`echo $f | cut -d "/" -f2 |cut -d'_' -f1 | tr a-z A-Z`
        	echo -e "\n====="$LPName"===== "		
                awk -f /tmp/mixedprice.awk $f
        done
        
}
RUN_TIME=`date +%Y%m%d_%H%M%S`
LIST=
CFG=
CONNECTIVITY=
SIMFIX=
BINARY=
OUTPUT_DIR=
MULTIPROCESS=
HBtime=
VERBOSE=
WAIT=
FTT_BINARY=

while getopts “hl:c:n:i:s:f:o:b:S:mt:vw” OPTION
do
	if [[ $OPTARG == -* ]] # && [[ $OPTION <> h ]] && [[ $OPTION <> m ]] && [[ $OPTION <> v ]] && [[ $OPTION <> w ]]
	then
		echo "$0: ---- option requires an argument -- $OPTION"
		usage
		exit 1
	else 
		


	case $OPTION in
		h)
			usage
			exit 1
			;;
		l)
			LIST=$OPTARG
			;;
		c)
			CFG=$OPTARG
			;;
		n)
			CONNECTIVITY=$OPTARG
			;;
		i)
			LIC=$OPTARG
			;;
		s)
			SIMFIX=$OPTARG
			;;
		f)
			BINARY=$OPTARG
			;;
		o)
			OUTPUT_DIR=$OPTARG/$RUN_TIME/
			;;
		v)
			VERBOSE=1
			;;
		w)
			WAIT="-w"
			;;
		m)
			MULTIPROCESS=1
			;;
		t)
			time=$OPTARG
			;;
		b)
			HBtime=$OPTARG
			;;
		S)
			STRESS="-s $OPTARG"
			;;
		?)
			usage
			exit
			;;
	esac
	fi
done
if [[ -z $LIST ]] || [[ -z $CFG ]] || [[ -z $SIMFIX ]] || [[ -z $BINARY ]] || [[ -z $OUTPUT_DIR ]]
then
	usage
	exit 1
fi

a=`echo ${BINARY##*/}|grep -i ftt`
b=`echo ${BINARY##*/}|grep -i fixation`
if [[ $a ]]
then
	FTT_BINARY=1
	if [[ $b  ]]
	then
		echo "the name of the binary is inconclusive"
		usage
		exit 1
	fi
fi


if [[ $MULTIPROCESS ]] && [[ $FTT_BINARY ]]
then
	echho "You cannot use MultiProcess and Ftt together"
	usage
	exit 1
fi

if [[ -z $time ]]
then
	time=50400
fi

if [[ -z $HBtime ]]
then
	HBtime=28000
fi


setup $VERBOSE
echo "Output directory: "$OUTPUT_DIR

if [ $FTT_BINARY ]
then
	Run_SimFix
	Run_Ftt
elif [ $MULTIPROCESS ]
then
	Run_FIXation
	Run_SimFix
	Login_N_Connect
else
	Run_SimFix
	Run_FIXation
fi


COUNT=0
#cat /var/log/messages > $OUTPUT_DIR/tmp
#echo "UID        PID  PPID  C STIME TTY          TIME CMD"
while true
do
   FH=`ps -ef|grep $PIDOF_BINARY|grep -v grep`
   SIM=`ps -ef|grep $PIDOF_SIMFIX|grep -v grep`
   #fh_str=$([ "$FTT_BINARY" ] && echo "Ftt" || echo "FIXation")
   if [ -z "$FH" ]
   then
      echo "Binary failed. "
      END_FIXATION=$(date +%s)
      DIFF=$(( $END_FIXATION - $START_FIXATION ))
      echo "FIXation was alive " $DIFF "seconds"
      cat /var/log/messages | grep $PIDOF_BINARY > current_syslog
      cat current_syslog | egrep -i "TIMEOUT|fault" 
      kill -9 $PIDOF_SIMFIX
      #echo "build2go!" | sudo -s kill -9 $PIDOF_SIMFIX
      ATEMPT=0
      sleep 10
      SIM=`ps -ef|grep $PIDOF_SIMFIX|grep -v grep`
      while [ "$SIM" ]
      do
          echo "simfix is still up"
          kill -9 $PIDOF_SIMFIX
          ((ATEMPT++))
          if [ $ATEMPT == 6 ]
          then
              echo "SimFix is zombie"
              break
          fi
          sleep 10
          SIM=`ps -ef|grep $PIDOF_SIMFIX|grep -v grep`
      done
      echo "Finished at: `date +%D_%T:%N` "
      #echo `tail $OUTPUT_DIR/${fh_str}_screen.log`
      echo "NOT OK - binary failed"
      echo SANITY_FINAL_RESULT 2
      sleep 20
      coref=`ls /var/crash | grep $PIDOF_BINARY`
      if [[  ! -z $coref ]]
      then
         echo -e "Core was dumped:\n " 
         FIXATION_REVISION=`$BINARY -v | grep "FIXation version" | awk '{print $3}'` 
         echo -e "gdb" $BINARY"."$FIXATION_REVISION " /var/crash/"$coref
      else
         echo "FIXation failed w/o core. Probably configuration error"
      fi

	   FIX_ERROR=`egrep -m 1 "segfault|coredump" $OUTPUT_DIR/current_syslog`
      #echo $FIX_ERROR
      if [[ ! -z $FIX_ERROR ]]
      then
         echo $FIX_ERROR
         echo "errors found in ftt log - see current_syslog"
      fi

      exit 2
   fi

   if [ -z "$SIM" ]
   then
      END_SIMFIX=$(date +%s)
      DIFF=$(( $END_SIMFIX - $START_SIMFIX ))
      echo "simfix life: "$DIFF
      if  [ $DIFF -gt 500 ]
      then
            echo "The time is over...Shutting down..."
      else
            echo "Sanity failed due to simfix issue"
            echo SANITY_FINAL_RESULT 2
            exit 2

      fi
      kill -9 $PIDOF_BINARY
      ATEMPT=0
      sleep 10
      FH=`ps -ef|grep $PIDOF_BINARY|grep -v grep`
      while [ "$FH" ]
      do
          echo "$fh_str is still up"
          kill -9 $PIDOF_SIMFIX
          ((ATEMPT++))
          if [ $ATEMPT == 6 ]
          then
              echo "$fh_str is zombie"
              cat /var/log/messages | grep $PIDOF_BINARY > current_syslog
              break
          fi
          sleep 10
          FH=`ps -ef|grep $PIDOF_BINARY|grep -v grep`
      done
      echo "OK. The test  is finished !"
		#diff /var/log/messages $OUTPUT_DIR/tmp > $OUTPUT_DIR/syslog
      #diff /var/log/messages OUTPUT_DIR/tmp | grep ">" > f
      #comm -3 /var/log/messages $OUTPUT_DIR/tmp > myfile
      cat /var/log/messages | grep $PIDOF_BINARY > current_syslog
		sleep 10
	  echo SANITY_FINAL_RESULT 0
      break
   fi
   if [ $[$COUNT % 30] = 0 ]
   then
      echo "==  "`date +%D_%T:%N` " ==script  is still running..."
#      echo $FH
#      echo $SIM
   fi
   sleep 10
   COUNT=$[$COUNT + 1]
done
Verify
echo "Finished at: `date +%D_%T:%N`"

