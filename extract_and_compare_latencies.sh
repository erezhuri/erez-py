#!/bin/bash
if [ -z "$1" ]
then
	echo "please specify file name to analyze"
	exit 1
fi

fn="$1"

## PREPARED  LIST OF LATENCIES ##
declare -A baseline_latencies
#rounded down
baseline_latencies[barx]=23
baseline_latencies[bnpp]=22
baseline_latencies[bofa]=15
baseline_latencies[citi]=21
baseline_latencies[commerz]=18
baseline_latencies[currenex]=23
baseline_latencies[fastmatch]=17
baseline_latencies[fxall]=16
baseline_latencies[fxspotstream]=22
baseline_latencies[gs]=56
baseline_latencies[gtx]=23
baseline_latencies[hotspot]=23
baseline_latencies[hsbc]=26
baseline_latencies[mizuho]=39
baseline_latencies[ms]=16
baseline_latencies[rbc]=25
baseline_latencies[rbs]=20
baseline_latencies[socgen]=33
baseline_latencies[ubs]=71

declare -Ag latencies
# we can't do everything in pipes, this makes vars local, so we out to file and then read it
sed -n /'Rates latency'/,/'Rates latency: how'/p $fn | grep "[0-9]$"  | sort -k 1 | awk '{print $1, $6}' | tr " " \\012 > /tmp/$fn

while read lp; do 
	read lat
	lat1=`echo $lat|sed s/"\..*"//` # round down
	latencies[$lp]=$lat1
	#echo "$lp - $lat"
	#latencies[$lp]=$lat
	echo "${#latencies[@]}: $lp --> ${latencies[$lp]} while in base its ${baseline_latencies[$lp]}"
done < /tmp/$fn


#latencies[socgen]="0"
#echo "total ${#latencies[@]} latencies as opposed to ${#baseline_latencies[@]}"
#echo "${baseline_latencies[@]}"
set status=0

for lp in "${!latencies[@]}"
do
	#some sanity because i'm so good at heart :D

	if [ -z ${baseline_latencies[$lp]} ]; then
		echo "$lp doesn't have base latency, please add to list in this script $0"
		status=1
		continue
	fi

	if [ ${latencies[$lp]} -eq 0 ]; then
		echo "Can't work with latency 0 on $lp, check your file $fn"
		status=1
		continue
	fi

	# we want 20%, so if old is less than 80 of the old..
	if [[ $((100*${baseline_latencies[$lp]}/${latencies[$lp]})) -lt 80 ]]; then
		echo "$lp: now ${latencies[$lp]}, base ${baseline_latencies[$lp]}"
		status=1
		fi
done

rm /tmp/$1 -f

exit $status
