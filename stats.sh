#!/usr/bin/env bash
echo > stats.out
for TAG_DATE in $(git tag --sort=creatordate  --format='%(refname:short),%(creatordate:short)'); do
    split=(${TAG_DATE//,/ })
    git checkout tags/${split[0]} readmeData.json 
    entries=$(jq '.base.entries' readmeData.json)
    echo ${split[1]},${entries} >> stats.out
done
