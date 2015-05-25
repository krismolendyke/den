#!/bin/sh

# Installed to root's crotab with schedule:
# 20 15 * * * /home/ec2-user/pyden/backup.sh

START=$(/bin/date +%s)
/sbin/service influxdb stop
/bin/tar -cjf /tmp/den-shared.tbz /opt/influxdb/shared
/sbin/service influxdb start
echo "InfluxDB down during archive creation for" $(($(/bin/date +%s) - $START)) "seconds"

UPLOAD_START=$(/bin/date +%s)
/usr/bin/aws s3 cp /tmp/den-shared.tbz s3://den.k20e.com
echo "Upload completed in" $(($(/bin/date +%s) - $UPLOAD_START)) "seconds"
echo "Backup completed in" $(($(/bin/date +%s) - $START)) "seconds"
