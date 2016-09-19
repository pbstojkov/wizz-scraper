#!/bin/bash

r=$RANDOM
sleep $((r%10*60))
python3 /home/osmc/code/wizzscrape/wizzscrape.py
