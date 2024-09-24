#!/bin/bash

source_path="src"
dest_path="pointage"
if [ ! -z $1 ];
then
	source_path=$1
	dest_path=$2
fi

python3 -m zipapp $source_path -o $dest_path -p "/usr/bin/python3" -c
