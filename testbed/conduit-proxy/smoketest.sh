trap "echo 'FAILED!'; exit 1" ERR
set -x
set -eu
set -o pipefail

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

conduitproxy="$(pwd)/../../proto/conduit-proxy"
arcyon="$(pwd)/../../bin/arcyon"

$conduitproxy -h

phaburi="http://127.0.0.1"
phabuser='phab'
phabcert=xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrv\
afgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w\
6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk\
3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf

$conduitproxy\
    --uri ${phaburi}\
    --user ${phabuser}\
    --cert ${phabcert}\
    --port 8118\
    &

conduitproxypid=$!
trap "echo 'FAILED!'; kill $conduitproxypid; exit 1" ERR
conduitproxyuri='http://127.0.0.1:8118'

# $arcyon query\
#     --uri $conduitproxyuri\
#     --user ${phabuser}\
#     --cert ${phabcert}\
#     --max-results 1

$arcyon query\
    --uri $conduitproxyuri\
    --user phab\
    --cert blerg\
    --max-results 1

trap - ERR
kill $!
echo OK
