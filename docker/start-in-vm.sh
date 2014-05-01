#!/bin/bash
source /etc/apache2/envvars
set -x
apache2 -D FOREGROUND &
mysqld_safe &
sleep 3
mysql < /initial.db
/var/www/phabricator/phabricator/bin/storage upgrade --force
sleep infinity
