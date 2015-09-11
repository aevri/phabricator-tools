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
# -----------------------------------------------------------------------------
# Copyright (C) 2015 Bloomberg Finance L.P.
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
