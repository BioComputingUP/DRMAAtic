#!/bin/bash
###
echo "I'm job array ${SLURM_ARRAY_TASK_ID}, hello!" >> output
rnd=10
yes > /dev/null &
ypid=$!
sleep $rnd
{ kill $ypid && wait $ypid; } 2>/dev/null
####
# Prepare output files in a zip
####
if [[ ${SLURM_ARRAY_TASK_ID} == "${SLURM_ARRAY_TASK_MAX}" ]]; then
  zip ../../downloads/"$(basename "$PWD")".zip ./* >/dev/null
fi
