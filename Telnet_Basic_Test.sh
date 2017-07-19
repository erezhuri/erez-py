#!/bin/sh

# the  set of soubroutines below/above help to test the FIXation envitonment #
# two ways are appearing for that. 1) randlomly test issues. 2) specifically #
# test the things related to certain Jira items,  for example                #
# Please note, that what is tested is easily modified via chaning the items  #
# strings of arrya, right before the command is exectuted.                   #
# As indicated, either random, or fixed execeution is possible, by restrictin#
# the RANDMO number generator with each command                              #

#veryfication commands can be added to test exactly type of things one would #
#like to test. These verification routes can be written in any language      #
# and called right after the completion of each telnet command               #
# for verification to be done independently of telnet session, which terminates#
#immediately after execution, on may want to direct each command out put to #
#file and process with a processor of his/her choice






## show all disconnected lps 
status_all ()
{
	echo "(echo "clear"; echo "fs"; sleep 1;) | telnet $HOST $PORT > status_all.tln"
	(echo "clear"; echo "fs"; sleep 1;) | telnet $HOST $PORT > status_all.tln
	if [[ $1 ]];then
		echo "non-connected LP's:"
		cat status_all.tln | grep "not-connected" | sort -u | awk ' { print $1 }' 
	fi
}
	
#show all disconnected lp from the list
status_lp ()
{
	#LP_FILE=$1;
	#echo $LP_FILE;
	sleep 2;	
	(echo "clear"; echo "fs"; sleep 5;) | telnet $HOST $PORT > status_list.tln
	if [[ $1 ]];then
		echo "non-connected LP's:"
		for i in $LP_LIST
		do
			grep $i status_list.tln | grep "not-connected" | sort -u | awk ' { print $1 }'
		done
	fi
}

## run info on all active LPs from the list
info_lp()
{
	status_lp
	for i in $LP_LIST
	do
		lp=grep -v "not-connected" status_list.tln | sort -u | awk ' { print $1 }'
		(echo "clear"; echo "info $lp"; sleep 2;) | telnet $HOST $PORT
	done
}

## randomly find an active lp and provide info for it
info_rand()
{
	status_all
	alllps=`cat status_all.tln|egrep -v "^[a-z]|^[A-Z]|>" |awk ' { print $1 }'|wc -l`
	rand=`echo $(( ( RANDOM % $alllps )  + 1 ))`
	lp=` cat status_all.tln|egrep -v "^[a-z]|^[A-Z]|>" |awk ' { print $1 }' |grep . -n |egrep "^$rand:"|awk -F\: ' { print $2} '`
	(echo "clear"; echo "info $lp"; sleep 2;) | telnet $HOST $PORT
	#verify_lpinfo
}

## randomly display top of book
topOfBook_rand()
{
	curr[1]='eurusd';
	curr[2]='eurgbp';
	curr[3]='eurjpy';
	#curr[4]='aud';
	rand=`echo $(( ( RANDOM % 3 )  + 1 ))`
	echo $rand;
	#output lines with "empties"
	(echo "clear"; echo "afr ${curr[$rand]}"; sleep 3;) | telnet $HOST $PORT | grep bid | egrep -v "[0-9]"
	#second way using awk
	# cat book.tln | grep bid | awk '{ if (NF < 6) print }'
	
}



# show top of book  for ccp's from the list
topOfBook_ccp()
{
	for i in `cat $CCP` ;do 
		#output lines with "empties"
		(echo "clear"; echo "afr $i"; sleep 3;) | telnet $HOST $PORT | grep bid | egrep -v "[0-9]" # > book.tln
		#grep bid book.tln 
	done
	#second way using awk
	# cat book | grep bid | awk '{ if (NF < 6) print }'
	
}

## randomly display full book
books_rand()
{
	curr[1]='eurusd';
	curr[2]='eurgbp';
	curr[3]='eurjpy';
	#curr[4]='aud';
	rand=`echo $(( ( RANDOM % 3 )  + 1 ))`
	echo $rand;
	(echo "clear"; echo "afr ${curr[$rand]}"; sleep 5;) | telnet $HOST $PORT> fullbook.tln
	max=`cat fullbook.tln|awk '{print $5}'|sort|egrep "[0-9]" | tail -1`;
	echo $max;
	min=`cat fullbook.tln|awk '{print $5}'|sort|egrep "[0-9]" | head -1`;
	echo $min;
	let "d=$min*100/$max";
	echo $d;
	if [ "$d" -lt "98" ]; then
		echo "switched values in FB: ";
		cat fullbook.tln;
	#	cat fullbook.tln | awk '{if(NF==2){str=$1"_"$2};if($4>555 && NF>2){print str ": " $0}}'
	fi
	#verify_full_book
}


## display full book according to ccp
verify_switched_ccy()
{
	#ccp=$1;
	for i in `cat $CCP` ;do
		(echo "clear"; echo "afr ^$i"; sleep 5;) | telnet $HOST $PORT > fullbook.tln
		#cat fullbook.tln
		echo $i
		zeroVol=`cat fullbook.tln|awk '{print $7}' fullbook.tln|sort -u|egrep "[0-9]" |head -1 `;
		#echo `cat fullbook.tln|awk '{print $7}' fullbook.tln|sort -u|egrep "[0-9]" |head -1 `
		if [[ $zeroVol == '0' ]];then
			echo we have zero volum				
			cat fullbook.tln
		fi
		max=`cat fullbook.tln|awk '{print $5}' fullbook.tln|sort|egrep "[0-9]" | tail -1`;
		echo max $max;
		min=`awk '{print $5}' fullbook.tln|sort|egrep "[0-9]" | head -1`;
		echo min $min;
		let "d=$min*100/$max";
		echo $d;
		if [ "$d" -lt "96" ]; then
			echo "switched values in FB: ";
		#        cat fullbook.tln;
		#       cat fullbook.tln | awk '{if(NF==2){str=$1"_"$2};if($4>555 && NF>2){print str ": " $0}}'
		fi
	done
	#verify_full_book
}



buildTrades()
{
	#VOL="1m"
	ALL_TIF=( ioc day fok )
	ALL_OT=( pq limit market )
	for lp in $LP_LIST;do
		for TIF in "${ALL_TIF[@]}";do
			for OT in "${ALL_OT[@]}";do
				for ccy in `cat $CCP`;do
					for VOL in 500000 1m 3m 5m 10m;do
						echo "buy $lp $ccy $VOL $OT $TIF" >> trade_orders.tln
						echo "sell $lp $ccy $VOL $OT $TIF" >> trade_orders.tln
						echo "buyv $lp $ccy $VOL $OT $TIF" >> trade_orders.tln
						echo "sellv $lp $ccy $VOL $OT $TIF" >> trade_orders.tln
					done
				done
			done
		done
	done
	echo Done building comands
}

####  Random trading  ####
trade_rand()
{

	range="`cat trade_orders.tln|wc -l`"
	j=1
	while read line ; do 
		order[$j]=$line
		#echo "criating-$j - $line to: ${order[$j]}" 
		((j++))
	done < trade_orders.tln
	#for i in "`cat trade_orders.tln`";do
	#	order+=($i)
	#	echo "criating-$j - $i to: ${order[$j]}"
	#	((j++))
	#done
	#echo "range: $range , len: ${#order[@]}"
	#rand=$(( ( RANDOM % ${#order[@]} )  + 1 ))
	#echo "$rand"
	#echo "running:    ${order[$rand]}"

	while true;do
		rand=$(( ( RANDOM % $range )  + 1 ))
		echo "running - $rand:    ${order[$rand]}"
		(echo "clear"; echo "${order[$rand]}"; sleep 60;) | telnet $HOST $PORT | grep -v "logged-in"
	done
}

####  Serial trading  ####
trade()
{
	for i in "`cat trade_orders.tln`";do
		echo "$i"
		(echo "clear"; echo "$i"; sleep 60;) | telnet $HOST $PORT | grep -v "logged-in"
		sleep 60
	done
}


####################  Parse parameters   #########################

usage()
{
cat << EOF
usage: $0 options

This script run FIXation/FTT with SimFix

OPTIONS:
   -h      Show this message
   -l      List of LPs 
   -c      ccy pais list
   -i      ip of host (default localhost)
   -p      port (default 60000)
   -r      run random tradeing
   -v      Verbose

EOF
	#turn this on if you run Ftt Binary (do not work wuth -m)
}

RUN_TIME=`date +%Y%m%d_%H%M%S`
LP_FILE=
CCP=
HOST=
PORT=
RAND=
VERBOSE=

while getopts “hl:c:i:p:rv” OPTION
do
	# Check if we there is a valid value to options that are not just flags 
	if [[ $OPTARG == -* ]];	then
		if [[ -z $TERM ]];then echo "$0: ---- option requires an argument -- $OPTION" 
		else echo "$(tput setaf 1)$0: ---- option requires an argument -- $OPTION$(tput sgr 0)";fi
		usage
		exit 1
	else 
		

	case $OPTION in
		h)
			usage
			exit 1
			;;
		l)
			LP_FILE=$OPTARG
			;;
		c)
			CCP=$OPTARG
			;;
		i)
			HOST=$OPTARG
			;;
		p)
			PORT=$OPTARG
			;;
		r)
			RAND=1
			;;
		v)
			VERBOSE=1
			;;
		?)
			usage
			exit
			;;
	esac
	fi
done
if [[ -z $CCP ]]; then
	usage
	exit 1
fi

if [[ -z $HOST ]];then
	HOST="localhost"
fi

if  [[ -z $PORT ]];then
	PORT=60000
fi

if [[ -z $LP_FILE ]];then
	status_all
	LP_LIST=`grep -v "not-connected" status_all.tln | sort -u | awk ' { print $1 }'`
	#echo "hotspot socgen rbc gs dbab ms bofa rbs ads gtx integral fastmatch fxspotstream ebsai1 currenex citi fxall mizuho barx hsbc bnpp commerz ubs saxo bmpx jpm" > LP.tln
	#LP_FILE="$PWD/LP.tln"
	echo "using default LP list $LP_LIST"
else
	LP_LIST="`cat $LP_FILE`"
fi

#==== End of Parse parameters   ====#


###################################    MAIN   #############################

rm -f *.tln

#export LP_FILE=$1;
#export CCP=$2;
#echo run status all
#status_all 1;


echo run LP status
status_lp 1;
echo run show TOB
topOfBook_ccp;
echo run show full book
verify_switched_ccy
buildTrades
if [[ $RAND ]];then
	echo run random trades
	trade_rand
else
	echo run serial trades
	trade
fi



