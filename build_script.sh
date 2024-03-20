#!/bin/bash

cd src
zip -r ../pointage.zip *
cd ..

echo "#!/usr/bin/python3" | cat - pointage.zip > pointage
chmod a+x pointage

rm pointage.zip
