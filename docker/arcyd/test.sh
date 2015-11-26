set -eux

# NOTE: this script expects you to have phab running in a local container
# called 'phab-web', serving http.

docker kill git
docker rm git
docker run -d --name git gitdaemon arcyd a b c
docker kill arcyd
docker rm arcyd
../build-image.sh arcyd-dockerfile arcyd
docker run -d --name arcyd arcyd git://git/arcyd

# wait for arcyd container to be ready
while ! docker exec arcyd arcyd-do list-repos 2> /dev/null; do sleep 1; done

docker exec arcyd arcyd-do add-repohost --name mygit

phaburi="http://phab-web"
arcyduser='phab'
arcydcert=xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrv\
afgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w\
6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk\
3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf

docker exec arcyd arcyd-do add-phabricator \
    --name phabweb \
    --instance-uri "$phaburi/api/" \
    --review-url-format '$phaburi/D{review}' \
    --admin-emails 'local-phab-admin@localhost' \
    --arcyd-user "$arcyduser" \
    --arcyd-cert "$arcydcert"

docker exec arcyd arcyd-do add-repo phabweb mygit git://git/a
docker exec arcyd arcyd-do add-repo phabweb mygit git://git/b
docker exec arcyd arcyd-do add-repo phabweb mygit git://git/c
docker exec arcyd arcyd-do reload

docker logs arcyd
sleep 5
docker exec arcyd cat var/arcyd/var/log/debug
