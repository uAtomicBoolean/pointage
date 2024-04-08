#!/bin/bash

source_path="src"
if [ ! -z $1 ];
then
	source_path=$1
fi

python3 -m zipapp $source_path -o pointage -p "/usr/bin/python3" -c
