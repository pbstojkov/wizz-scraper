#!/bin/bash

FILES=/home/osmc/code/wizzscrape/SettingFiles/*.in
cd /home/osmc/code/wizzscrape/
for f in $FILES
do
  r=$RANDOM
  sleep $((r%10*60))
  # arguments: file_name save_images save_html
  python3 wizzscrape.py $f 0 0
done
