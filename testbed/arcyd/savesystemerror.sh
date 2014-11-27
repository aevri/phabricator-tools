#! /usr/bin/env bash

###############################################################################
# for use with arcyd, to simply save reported errors to disk
###############################################################################

set +x  # DONT echo all commands to the terminal
set -e  # exit with error if anything returns non-zero
set -u  # exit with error if we use an undefined variable

echo $1 >> system_error.log
echo $2 >> system_error.log
echo >> system_error.log
