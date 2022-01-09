#!/bin/sh

riskhub_new_build_folder=$1
rev=$(/home/jenkins/workspace/verify_-t_TENS/$riskhub_new_build_folder/riskhub -v | grep "Svn Revision" | awk -F " " '{print $3}')
/home/jenkins/workspace/verify_-t_TENS/$riskhub_new_build_folder/riskhub -t -ini /etc/ftt/riskhub_49_54.cfg -cfg /etc/ftt/tensInFixation/tensStreamNoRisk.cfg > /tmp/res_TENS_-t.log 2>&1
res=$(grep "result of test mode" /tmp/res_TENS_-t.log | awk -F " " '{print $5}')
res="$(echo -e "${res}" | tr -d '[[:space:]]')"
if [ "$res" == "PASS" ]; then
  echo "cfg for RiskHub + TENS revision $rev - PASS."
  exit_status=0
else
  echo "cfg for RiskHub + TENS revision $rev - FAIL."
  echo "==============================="
  cat /tmp/res_TENS_-t.log
  exit 1
fi

