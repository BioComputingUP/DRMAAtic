#!/bin/bash
date1=$(date +"%s")
echo "Started " "$(date)"
blastp $1
date2=$(date +"%s")
DIFF=$((date2-date1))
echo "Duration: $((DIFF / 3600 )) hours $(((DIFF % 3600) / 60)) minutes $((DIFF % 60)) seconds"
