#! /usr/bin/env bash
THIS_DIR=$(cd $(dirname $0); pwd -P)
echo ${THIS_DIR}
BUILD_DIR=$(mktemp -d)

pushd ${BUILD_DIR}
cp -R "${THIS_DIR}/../.." ${BUILD_DIR}
mv testbed/pox/pox-dockerfile Dockerfile
docker build -t pox .
popd

rm -rf ${BUILD_DIR}
