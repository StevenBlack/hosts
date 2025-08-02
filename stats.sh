#!/usr/bin/env bash

# clear file
true > stats.out

for TAG_DATE in $(git tag --sort=creatordate  --format='%(refname:short),%(creatordate:short)'); do
  # echo "$TAG_DATE"
  split=(${TAG_DATE//,/ })
  # echo ${split[0]}
  entries=$(git show tags/${split[0]}:readmeData.json | jq '.base.entries')
  if [[ -z "$entries" ]]; then continue; fi
  echo ${split[1]},${entries} >> stats.out
done
