#!/bin/bash

# batch add stake
num=${1:-10}

for i in $(seq 1 $num); do
    echo "Adding stake $i of $num"
    python manage/stake_add.py --network test  --amount 0.001 --partial
done