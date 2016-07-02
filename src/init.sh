#!/bin/sh

trap '' 2
basedir=$(dirname $0)

export LANG='zh_CN.UTF-8'
python $basedir/connect.py

exit