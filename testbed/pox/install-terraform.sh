#! /usr/bin/env bash
BUILD_DIR=$(mktemp -d)

pushd ${BUILD_DIR}
wget https://dl.bintray.com/mitchellh/terraform/terraform_0.6.0_linux_amd64.zip
unzip *.zip
rm *.zip
sudo mkdir /opt/terraform
sudo mv * /opt/terraform
sudo ln -s /opt/terraform/terraform /usr/bin/
popd

rm -rf ${BUILD_DIR}
