#! /bin/sh
docker run -d --name phab-mysql --hostname phab-mysql -e MYSQL_ALLOW_EMPTY_PASSWORD=yes mysql
