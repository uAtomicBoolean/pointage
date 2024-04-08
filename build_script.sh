#!/bin/bash
# You can specify the destination path of the script as an argument.

file_dest="pointage"
if [ ! -z $1 ];
then
	file_dest=$1
fi

python3 -m zipapp src -o $file_dest -p "/usr/bin/python3" -c
