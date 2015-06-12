#!/bin/sh

ARCHIVE=${1}
BUCKET=${2}

START=$(/bin/date +%s)
/sbin/service influxdb stop
/bin/tar -cjf ${ARCHIVE} /opt/influxdb/shared
/sbin/service influxdb start
echo "InfluxDB down during archive creation for" $(($(/bin/date +%s) - $START)) "seconds"

UPLOAD_START=$(/bin/date +%s)
/usr/bin/aws s3 cp ${ARCHIVE} ${BUCKET}
echo "Upload completed in" $(($(/bin/date +%s) - $UPLOAD_START)) "seconds"
echo "Backup completed in" $(($(/bin/date +%s) - $START)) "seconds"
