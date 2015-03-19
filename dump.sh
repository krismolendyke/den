#!/bin/sh

function dump() {
    echo "Dumping ${1}…"
    time /home/ec2-user/den/dump.py ${1} --port 8087 --ssl --bucket den.k20e.com
}

source /usr/bin/virtualenvwrapper.sh
workon den
dump "grafana"
dump "den"
