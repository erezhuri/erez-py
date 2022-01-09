#/usr/bin/bash

#cd /var/log/fixation

CurrentDate=`date +"%Y%m%d"`
__use_only_in_finction_assert__=false

assert ()
{
  actual=$1
  expected=$2
  errorMessage=$3

  if [ $actual -eq $expected ]; then
    a=1
  else
    if [ "$__use_only_in_finction_assert__" = "false" ]; then
      echo
      echo " * * * FAIL * * * "
      __use_only_in_finction_assert__=true
    fi
    echo -ne $errorMessage
    echo -ne " expected: " $expected
    echo -ne " actual: " $actual
    echo
  fi
}

echo
echo "* * * START TESTING STREAM CLIENT FOR EBSAI * * *"
echo
# place order stream client
numOfPlaceOrders=$(grep 35=D sc1_trade_$CurrentDate.log | wc -l)

assert $numOfPlaceOrders 12 "Stream Client: missing some place orders"

# Fill stream client
numOfFill=$(grep 35=8 sc1_trade_$CurrentDate.log | grep 150=F | grep 39=2 | wc -l)

assert $numOfFill 6 "Stream Client: missing some Fills"

# Reject Time Delay not multiply
numOfRejct=$(grep 35=8 sc1_trade_$CurrentDate.log | grep 150=8 | grep 39=8 | grep "should be be a multiple of Iceber" | wc -l)

assert $numOfRejct 1 "Stream Client: missing Reject multiply Iceberg"

# Reject Time Delay less then minimum
numOfRejct=$(grep 35=8 sc1_trade_$CurrentDate.log | grep 150=8 | grep 39=8 | grep "should not be less" | wc -l)

assert $numOfRejct 1 "Stream Client: missing Reject less from minimum amount"

# Reject Show amount smaller from minimum.
numOfRejct=$(grep 35=8 sc1_trade_$CurrentDate.log | grep 150=8 | grep 39=8 | grep "smaller than iceberg Minimum" | wc -l)

assert $numOfRejct 1 "Stream Client: Reject Show amount smaller from minimum."

# Reject Order Type is IOC
numOfRejct=$(grep 35=8 sc1_trade_$CurrentDate.log | grep 150=8 | grep 39=8 | grep "Invalid Order Type." | wc -l)

assert $numOfRejct 1 "Stream Client: Reject Order Type is IOC."

# Reject Order Type is IOC
numOfRejct=$(grep 35=3 sc1_trade_$CurrentDate.log | grep 371=210 | grep "use tags 1085,1086 for quantities." | wc -l)

assert $numOfRejct 2 "Stream Client: Reject not valid random iceberg order."


###################################################################

if [ "$__use_only_in_finction_assert__" = "false" ]; then
  echo
  echo " * * * PASS * * * "
  echo
else
  __use_only_in_finction_assert__=false  
fi

echo
echo "######################################"
echo

echo "* * * START TESTING EBSAI FEED HENDLER        * * *"

# place order ebsai
numOfPlaceOrders=$(grep 35=D ebsai_socket_$CurrentDate.log | wc -l)

assert $numOfPlaceOrders 10 "EBSAI: missing some place orders"

# Fill stream client
numOfFill=$(grep 35=8 ebsai_socket_$CurrentDate.log | grep 150=F | grep 39=2 | wc -l)

assert $numOfFill 6 "EBSAI: missing some Fills"

# Reject Time Delay not multiply
numOfRejct=$(grep 35=8 ebsai_socket_$CurrentDate.log | grep 150=8 | grep 39=8 | grep "should be be a multiple of Iceber" | wc -l)

assert $numOfRejct 1 "EBSAI: missing Reject multiply Iceberg"

# Reject Time Delay less then minimum
numOfRejct=$(grep 35=8 ebsai_socket_$CurrentDate.log | grep 150=8 | grep 39=8 | grep "should not be less" | wc -l)

assert $numOfRejct 1 "EBSAI: missing Reject less from minimum amount"

# Reject Show amount smaller from minimum.
numOfRejct=$(grep 35=8 ebsai_socket_$CurrentDate.log | grep 150=8 | grep 39=8 | grep "smaller than iceberg Minimum" | wc -l)

assert $numOfRejct 1 "EBSAI: Reject Show amount smaller from minimum."

# Reject Order Type is IOC
numOfRejct=$(grep 35=8 ebsai_socket_$CurrentDate.log | grep 150=8 | grep 39=8 | grep "Invalid Order Type." | wc -l)

assert $numOfRejct 1 "EBSAI: Reject Order Type is IOC."




if [ "$__use_only_in_finction_assert__" = "false" ]; then
  echo
  echo " * * * PASS * * * "
  echo
fi
echo "######################################"
