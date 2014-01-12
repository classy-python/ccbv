#!/bin/bash

if [ $# -ne 2 ]; then
    echo "usage: checkout_release.sh PATH RELEASE"
    exit 1
fi

cur=`pwd`
path="$1"
release="$2"

cd "$path"
tag=`git tag | grep "$release" | grep -v [a-z] | tail -1`
git checkout "$tag"
cd "$cur"
