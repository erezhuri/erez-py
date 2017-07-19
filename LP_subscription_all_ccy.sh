#/usr/bin/bash


# Usage: ./LP_subscription_all_ccy.sh <host> <potr> <LP> [1]

host=$1
port=$2
LP=$3
ACTION=$4

echo $host,$port,$LP



if [ -z "$ACTION" ]
then 

		ACTION="unsubscribe"
		echo $ACTION
else
		ACTION="subscribe"
		echo $ACTION
fi

CCY="EURUSD 
EURJPY 
EURGBP
USDJPY 
GBPUSD 
EURCHF 
USDCHF 
USDCAD 
AUDCAD 
AUDCHF 
AUDJPY 
AUDNZD 
AUDUSD 
CADCHF 
CADJPY 
CHFJPY 
EURAUD 
EURCAD 
EURNZD 
GBPAUD 
GBPCAD 
GBPCHF 
GBPJPY 
GBPNZD 
NZDJPY 
NZDUSD"

(
for i in  $CCY;
do
		echo "clear";
		sleep 1 ;
		echo "$ACTION $LP $i" ;
		sleep 3 ;
done) | telnet $host $port

