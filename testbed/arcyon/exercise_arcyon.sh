trap "echo 'FAILED!'; exit 1" ERR
set -x

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

arcyon='../../bin/arcyon'

$arcyon -h
$arcyon comment -h
$arcyon comment-inline -h
$arcyon get-diff -h
$arcyon paste -h
$arcyon query -h
$arcyon raw-diff -h
$arcyon show-config -h
$arcyon update-revision -h
$arcyon task-create -h
$arcyon task-query -h

cert=xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrv\
afgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w\
6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk\
3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf

creds="--uri http://127.0.0.1 --user phab --cert $cert"

id="$($arcyon create-revision -t title -p plan --summary ssss -f diff1 --format-id $creds)"
$arcyon get-diff -r $id --ls $creds
$arcyon update-revision $id update -f diff2 $creds
$arcyon get-diff -r $id --ls $creds

$arcyon query --format-type ids $creds | grep $id
$arcyon query --ids $id --format-string '$summary' $creds | grep ssss
$arcyon query --format-type ids --order created $creds | grep $id
$arcyon query --format-type ids --order modified $creds | grep $id

diffid="$($arcyon raw-diff diff1 $creds)"
diffid2="$($arcyon raw-diff diff2 $creds)"
$arcyon get-diff -d $diffid --ls $creds
$arcyon get-diff -d $diffid2 --ls $creds
id2="$($arcyon create-revision -t title2 -p plan --diff-id $diffid --format-id $creds)"
id3=$($arcyon update-revision $id2 update --diff-id $diffid2 --format-id $creds)
$arcyon update-revision $id2 update --diff-id $diffid2 --format-url $creds
$arcyon update-revision $id2 update --diff-id $diffid2 --format-url --ccs phab --reviewers bob $creds

if [ "$id2" != "$id3" ]; then
    false
fi

$arcyon query --format-type ids $creds | grep $id2

$arcyon comment $id2 -m 'hello there!' $creds
$arcyon comment-inline $id2 --start-line 51 --end-line-offset 0 --filepath 'bin/arcyon' -m 'inline comment!' $creds
$arcyon comment-inline $id2 --start-line 51 --end-line-offset 0 --filepath 'bin/arcyon' -m 'old-side inline comment!' --left-side $creds
$arcyon comment $id2 --attach-inlines $creds

taskid=$($arcyon task-create 'exercise task-create' -d 'description' -p wish -o alice --ccs phab bob --format-id $creds)
$arcyon task-query $creds
taskid2=$($arcyon task-query --max-results 1 --format-ids $creds)

if [ "$taskid" != "$taskid2" ]; then
    false
fi

$arcyon task-create 'exercise task-create again' $creds
$arcyon task-update $taskid -m 'just a comment' $creds
$arcyon task-update $taskid -t 'exercise task-update' -d 'new description' -p low -o bob --ccs phab alice -m 'updated loads' $creds

$arcyon paste "test paste" -f diff1 $creds
# -----------------------------------------------------------------------------
# Copyright (C) 2013-2015 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
