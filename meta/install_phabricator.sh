set -e  # exit on error
sudo apt-get install puppet
sudo puppet module install puppetlabs/apache

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

(cd ../vagrant && ./puppet-apply.sh)
