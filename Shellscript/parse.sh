#!/bin/bash
filename='million_songs_metadata.csv'
oIFS=$IFS
IFS=","
shopt -s nocasematch
num=0
while read -r id title sond_id release artist_id artist_mbid artist_name duration familiarity hotttnesss year
do
  if [[ "$1" = "$artist_name" ]] && [[ $2 -le $year ]] && [[ $3 -ge $year ]]
  then
    echo $artist_name $year
    num=$((num+1))
  fi
done < $filename
echo "#:" $num
