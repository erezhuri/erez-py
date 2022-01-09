#!/usr/bin/bash
OUT_FILE="/tmp/_t_output/res_t.log"
FIXation_FOLDER="/home/jenkins/versions/FIXation/$1"
CFG_FOLDER="/home/jenkins/jcfx/$1/server/qa"
rev=$($FIXation_FOLDER/FIXation -v | grep svn | awk -F " " '{print $1}')
sudo $FIXation_FOLDER/FIXation -t $CFG_FOLDER/app_sa_2.cfg $CFG_FOLDER/venues.cfg $CFG_FOLDER/fstream.cfg $CFG_FOLDER/risk.lic  > $OUT_FILE 2>&1
res=$(grep "result of test mode" $OUT_FILE | awk -F ":" '{print $2}')
res="$(echo -e "${res}" | tr -d '[[:space:]]')"
if [ "$res" == "PASS" ]; then
  echo "cfg for revision $rev - PASS."
  exit_status=0
else
  echo "cfg for revision $rev - FAIL."
  echo "==============================="
  cat $OUT_FILE 
  exit 1
fi
