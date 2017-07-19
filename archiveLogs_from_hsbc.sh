#!/bin/bash



dateSetup()
{
	#ARCHIVE_TIME=`date --date="$INPUT_DATE" +_%H%M%S`
	ARCHIVE_DATE=`date --date="$INPUT_DATE" +%Y%m%d`
	LOGS_DEL_DATE=`date --date="${ARCHIVE_DATE} -${REMOVE_SAVED} days" +%Y%m%d`
	ARCH_DEL_DATE=`date --date="${ARCHIVE_DATE} -${REMOVE_ARCHIVED} weeks" +%Y%m%d`
	if [[ $VERBOSE ]]
	then
		echo INPUT_DATE: $INPUT_DATE
		echo ARCHIVE_DATE = $ARCHIVE_DATE
		echo LOGS_DEL_DATE = $LOGS_DEL_DATE
		echo LOG_DIR = $LOG_DIR
		echo ARCHIVE_PATH = $ARCHIVE_PATH
		echo ARCH_DEL_DATE = $ARCH_DEL_DATE
	fi	
	if [[ $TEST == 0 ]] 
	then
		ls ${LOG_DIR}/*${ARCHIVE_DATE}*.log
		exit 0
	fi
}

archive()
{
	STATUS=1
	[[ $VERBOSE ]] && echo --------------------------------- Create folders ------------------------------------
	mkdir -${VERBOSE}p $ARCHIVE_PATH/${ARCHIVE_DATE}${ARCHIVE_TIME}_logs/
	ls $ARCHIVE_PATH/${ARCHIVE_DATE}${ARCHIVE_TIME}_logs/ || exit 1
	[[ $VERBOSE ]] && echo --------------------------------- Move logs ------------------------------------
	mv -${VERBOSE}u ${LOG_DIR}/*${ARCHIVE_DATE}*.log ${ARCHIVE_PATH}/${ARCHIVE_DATE}${ARCHIVE_TIME}"_logs"/ || STATUS=  #exit 1
	[[ $VERBOSE ]] && echo --------------------------------- Archive logs ------------------------------------
	if [[ $STATUS ]]
	then
		cd ${ARCHIVE_PATH}
		for log in "${ARCHIVE_DATE}"*_logs/*.log
		do
			if [ ${REMOVE_SAVED} -eq 0 ]
			then
				tar --remove-files -zc${VERBOSE}f ${log}.tgz ${log}
			else
				tar -zc${VERBOSE}f ${log}.tgz ${log}
			fi
		done
	fi
}

deleteOld()
{
	[[ $VERBOSE ]] && echo --------------------------------- delete old ------------------------------------
	set -xe
	#rm -vrf ${ARCHIVE_PATH}/archive/FIXation/${LOGS_DEL_DATE}_log/*${LOGS_DEL_DATE}*.tgz
	if [ ${REMOVE_SAVED} -ge 0 ]
	then
		find $ARCHIVE_PATH/${LOGS_DEL_DATE}*_logs -type f -name "*.log" | xargs rm -${VERBOSE}rf
	fi
	if [ ${REMOVE_ARCHIVED} -ne 0 ]
	then
		find $ARCHIVE_PATH/ -type d -name ${ARCH_DEL_DATE}*_logs | xargs rm -${VERBOSE}rf
	fi
}

usage()
{
cat << EOF
usage: $0 options

This script run FIXation/FTT with SimFix

OPTIONS:
   -h      Show this message
   -l      location of logs to archive (default: /var/log/fixation/)
   -n      archive now and add time to destination folder name - <DATE>_<TIME>_logs instead of <DATE>_logs
   -a      archive folder - output directory (default: /home/qa/logs/archive/FIXation/)
   -d      date of logs to archive. e.g. "3 days ago" (default: yesterday)
   -r      remove archived logs (foler with tgz files) <REMOVE_ARCHIVED> weeks before archive (default: 0 - do not delete)
   -R      remove saved not archived logs (*.log files) <REMOVE_SAVED> days before archive (default: 2 | set to -1 to not delete)
   -v      Verbose

EOF
#turn this on if you run Ftt Binary (do not work wuth -m)
}

INPUT_DATE="yesterday"
LOG_DIR=/var/log/fixation
ARCHIVE_PATH=/home/qa/logs/archive/FIXation/
REMOVE_ARCHIVED=0
REMOVE_SAVED=2
ARCHIVE_DATE=
ARCHIVE_TIME=
LOGS_DEL_DATE=
ARCH_DEL_DATE=
TEST=
VERBOSE=

while getopts “l:a:d:r:R:T:nhv” OPTION
do
	if [[ $OPTARG == -* ]] 
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
			LOG_DIR=$OPTARG
			;;
		a)
			ARCHIVE_PATH=$OPTARG/
			;;
		d)
			INPUT_DATE=$OPTARG
			;;
		n)
			ARCHIVE_TIME=`date --date="now" +_%H%M%S`
			INPUT_DATE="now"
			;;
		T)
			TEST=$OPTARG
			;;
		r)
			REMOVE_ARCHIVED=$OPTARG
			;;
		R)
			REMOVE_SAVED=$OPTARG
			;;
		v)
			VERBOSE=v
			#set -xe
			;;
		?)
			usage
			exit
			;;
	esac
	fi
done


echo --------------------------------- Stert: `date` ------------------------------------
if [[ $TEST != 1 || $TEST == 0 ]] 
then
dateSetup
fi
if [[ $TEST != 2 ]] 
then
	archive
fi
if [[ $TEST != 3 ]] 
then
	deleteOld
fi

echo --------------------------------- finishd: `date` ------------------------------------
