#/usr/bin/bash




if (( $# == 0 )); then
  echo
  echo
  echo "Usage: $0 <api_maker file> <bid price> <ask price> "
  echo
  echo
  exit 1
fi




file=$1
bid_price=$2
ask_price=$3
sed -i "s/price_t *bidPrice *= *to_price_t *( *TICKS_TO_STANDARD_INT( *[[:digit:]]\+ *)/price_t bidPrice = to_price_t ( TICKS_TO_STANDARD_INT($bid_price)/g" $file
sed -i "s/price_t *askPrice *= *to_price_t *( *TICKS_TO_STANDARD_INT( *[[:digit:]]\+ *)/price_t askPrice = to_price_t ( TICKS_TO_STANDARD_INT($ask_price)/g" $file
