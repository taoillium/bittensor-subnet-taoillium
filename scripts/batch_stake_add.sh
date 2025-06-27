#!/bin/bash

# batch add stake
num=${1:-10}
echo "Adding $num stakes"
for i in {1..$num}; do
    python manage/stake_add.py --network test  --amount 0.001 --partial
done