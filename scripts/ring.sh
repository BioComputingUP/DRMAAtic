#!/bin/bash
###
date1=$(date +"%s")
echo "Started " "$(date)"
echo $PWD > /home/aledc/test
/home/aledc/.ring/bin/Ring $1
#/opt/miniconda3/envs/bio/bin/python /home/alessio/projects/submission_ws/scripts/ring_graph_exporter.py
date2=$(date +"%s")
DIFF=$((date2-date1))
echo "Duration: $((DIFF / 3600 )) hours $(((DIFF % 3600) / 60)) minutes $((DIFF % 60)) seconds"
####
# Prepare output files in a zip
####
zip ../../downloads/"$(basename "$PWD")".zip ./* > /dev/null
