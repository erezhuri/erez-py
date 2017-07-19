#/usr/bin/bash

if (( $# == 0 )); then
  echo "Usage: $0 <Jixi output file name> "
  exit 1
fi

lp_name=$(cat $1 | grep "ExecType =" -B 1 | grep lp | awk -F "lp: " '{print $2}' | awk -F "," '{print $1}' | sort | uniq)

for i in $lp_name; do cat $1 | grep "ExecType =" -B 1 | grep $i -A 1 > /tmp/jixi_$i.log; done;

echo "========================"		
for j in $lp_name; do
a=$(cat /tmp/jixi_$j.log | grep "ExecType = " | awk -F "ExecType = " '{print $2}' | awk -F "," '{print $1}' | sort | uniq)
echo $j
echo "--------------------"
for x in $a; do echo -n "$x   "; echo $(cat /tmp/jixi_$j.log | grep "ExecType = " | awk -F "ExecType = " '{print $2}' | awk -F "," '{print $1}' | grep $x | wc -l); done;
echo "========================"		
done

