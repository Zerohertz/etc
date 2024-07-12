df -P | grep -v ^Filesystem | awk '{sum += $2} END { print "전체 용량:\t" sum/1024/1024 " GB" }'
df -P | grep -v ^Filesystem | awk '{sum += $3} END { print "사용 용량:\t" sum/1024/1024 " GB" }'
df -P | grep -v ^Filesystem | awk '{sum += $4} END { print "남은 용량:\t" sum/1024/1024 " GB" }'

DISK_TOTAL=`df -P | grep -v ^Filesystem | awk '{sum += $2} END { print sum; }'`
DISK_USED=`df -P | grep -v ^Filesystem | awk '{sum += $3} END { print sum; }'`
DISK_PER=`echo "100*$DISK_USED/$DISK_TOTAL" | bc -l`
echo "$DISK_PER %"