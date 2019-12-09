#!/bin/sh
filename=720_1280_badcase_CENTER_INSIDE
filename=1080_1920_badcase_CENTER_INSIDE
srcDir=~/Desktop/
dstDir=~/Desktop/$filename

# if [ -d $srcDir ]; then
#     echo hello
#     rm -rf $srcDir/TupuDebug
# fi

# if [ ! -d $dstDir ]
# then
#     echo not exist
#     mkdir $dstDir
# else
#     echo exist
#     rm -rf $dstDir/*
# fi

# adb pull /sdcard/TupuDebug/ ~/Desktop/TupuDebug

awk '{print $7}' ~/Desktop/$filename.txt | while read line; do
echo $line.jpg
cp $srcDir/TupuDebug/$line.jpg $dstDir
done