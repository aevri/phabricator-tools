#! /bin/sh
docker run -d --name phab-web --hostname phab-web -p 80:80 phabricator
