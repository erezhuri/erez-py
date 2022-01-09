#/usr/bin/bash

if (( $# == 0 )); then
  echo
  echo
  echo "Usage: $0 <ccy 1> <ccy 2> <price buy for ccy 1> <price sell for ccy 1> <price sell for ccy 2>"
  echo "example: ./run_ebsai4.sh EUR/USD EUR/JPY 1.065 1.055 130.1 "
  echo
  echo
  exit 1
fi

echo DropOF
qmd DropOF
sleep 1

echo "AddOF 210=1000000"
   qmd AddOF 210=1000000
sleep 1

echo "* * * 1. order buy ebsai 10M gtc * * *"
echo "* * * expected to PASS           * * *"
   qmd order EBSA $1 buy limit gtc 10000000 $3
sleep 1

echo "* * * 2. order sell ebsai 10M gtc * * *"
echo "* * * expected to PASS           * * *"
   qmd order EBSA $1 sell limit gtc 10000000 $4
sleep 1

echo "* * * 3. order sell eur/jpy ebsai 10M gtc * * *"
echo "* * * expected to PASS           * * *"
   qmd order EBSA $2 sell limit gtc 10000000 $5
sleep 1

echo "* * * 4. order sell TIF=ioc               * * *"
echo "* * * expected to FAIL           * * *"
   qmd order EBSA $2 sell limit ioc 10000000 $5
sleep 1

echo DropOF
qmd DropOF
sleep 1

echo "AddOF 210=1000000 1084=1"
   qmd AddOF 210=1000000 1084=1
sleep 1

echo "* * * 5. order buy 1084 = 1 * * *"
echo "* * * expected to PASS           * * *"
   qmd order EBSA $1 buy limit gtc 10000000 $3
sleep 1

echo DropOF
qmd DropOF
sleep 1

echo "AddOF 210=500000  1084=1"
   qmd AddOF 210=500000 1084=1
sleep 1

echo "* * * 6. order buy 210 = 0.5M    * * *"
echo "* * * expected to FAIL           * * *"
   qmd order EBSA $1 buy limit gtc 10000000 $3
sleep 1

echo DropOF
qmd DropOF
sleep 1

echo "AddOF 210=1000000  1084=3 1085=2000000 1086=3000000"
   qmd AddOF 210=1000000 1084=3 1085=2000000 1086=3000000
sleep 1

echo "* * * 7. order buy 210 = 1M    * * *"
echo "* * * expected to PASS           * * *"
   qmd order EBSA $1 buy limit gtc 10000000 $3
sleep 1

echo DropOF
qmd DropOF
sleep 1

echo "AddOF 1084=3 1085=3000000 1086=2000000"
   qmd AddOF 1084=3 1085=3000000 1086=2000000
sleep 1

echo "* * * 8. order buy 210 = 1M    * * *"
echo "* * * expected to PASS   * * *"
   qmd order EBSA $1 buy limit gtc 10000000 $3
sleep 1

echo DropOF
qmd DropOF
sleep 1

echo "AddOF 210=1000000  1084=1 5007=1000                "
   qmd AddOF 210=1000000 1084=1 5007=1000                
sleep 1

echo "* * * 9. order buy delay=1sec. * * *"
echo "* * * expected to PASS   * * *"
   qmd order EBSA $1 buy limit gtc 10000000 $3
sleep 1

echo DropOF
qmd DropOF
sleep 1

echo "AddOF 210=1000000  1084=1 5007=1                "
   qmd AddOF 210=1000000 1084=1 5007=1 
sleep 1

echo "* * * 10. order delay=1msec.   * * *"
echo "* * * expected to FAIL   * * *"
   qmd order EBSA $1 buy limit gtc 10000000 $3
sleep 1

echo DropOF
qmd DropOF
sleep 1

echo "AddOF 210=1000000  1084=1 5008=1 5007=999                "
   qmd AddOF 210=1000000 1084=1 5007=999 5008=1 
sleep 1

echo "* * * 11. order buy delay=999msec. * * *"
echo "* * * expected to FAIL   * * *"
   qmd order EBSA $1 buy limit gtc 10000000 $3
sleep 1

q=$4
NEW_PRICE=$(awk "BEGIN {printf \"%.4f\",${q}*0.9}")

   qmd M - - $NEW_PRICE 20

echo DropOF
qmd DropOF
sleep 1

echo "AddOF 210=1000000"
   qmd AddOF 210=1000000
sleep 1

echo "* * * 12. modify order           * * *"
echo "* * * expected to PASS           * * *"
   qmd order EBSA $1 buy limit gtc 10000000 $3
sleep 1

