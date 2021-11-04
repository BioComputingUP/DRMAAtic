#!/bin/bash
###
echo "first" >> output
rnd=30
yes > /dev/null &
ypid=$!
sleep $rnd
{ kill $ypid && wait $ypid; } 2>/dev/null
####
# Prepare output files in a zip
####
zip ../../downloads/"$(basename "$PWD")".zip ./*
