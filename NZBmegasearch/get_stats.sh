#~ LOGNAME=/opt/usntssearch/NZBmegasearch/logs/nzbmegasearch.log

LOGNAME="$1"
DT=$2
if [ -z "$2" ]; then
	DT=`date +"%Y-%m-%d"`
fi

echo "~=~ NZBmegccasearcH LOG stats [$DT -- $LOGNAME and rotatedlog] ~=~"
rm /tmp/logstats
grep "$DT" $LOGNAME | grep 'WARPNGX: '  | awk '{print $9}' > /tmp/logstats
grep "$DT" $LOGNAME.1 | grep 'WARPNGX: '  | awk '{print $9}' >> /tmp/logstats
