#! /bin/sh
docker exec phab-web sh -c 'until mysql --host phab-mysql; do sleep 1; done'
docker exec phab-web /phabricator/instances/dev/phabricator/bin/config set mysql.host phab-mysql
docker exec phab-web sh -c 'mysql --host phab-mysql < /opt/phabricator-tools/vagrant/puppet/phabricator/files/initial.db'
docker exec phab-web /phabricator/instances/dev/phabricator/bin/storage upgrade -f
