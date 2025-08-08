#!/usr/bin/env bash

lists="
alternates/fakenews
alternates/fakenews-gambling
alternates/fakenews-gambling-only
alternates/fakenews-gambling-porn
alternates/fakenews-gambling-porn-only
alternates/fakenews-gambling-porn-social
alternates/fakenews-gambling-porn-social-only
alternates/fakenews-gambling-social
alternates/fakenews-gambling-social-only
alternates/fakenews-only
alternates/fakenews-porn
alternates/fakenews-porn-only
alternates/fakenews-porn-social
alternates/fakenews-porn-social-only
alternates/fakenews-social
alternates/fakenews-social-only
alternates/gambling
alternates/gambling-only
alternates/gambling-porn
alternates/gambling-porn-only
alternates/gambling-porn-social
alternates/gambling-porn-social-only
alternates/gambling-social
alternates/gambling-social-only
alternates/porn
alternates/porn-only
alternates/porn-social
alternates/porn-social-only
alternates/social
alternates/social-only
data/Badd-Boyz-Hosts
data/KADhosts
data/StevenBlack
data/URLHaus
data/UncheckyAds
data/adaway.org
data/add.2o7Net
data/add.Dead
data/add.Risk
data/add.Spam
data/hostsVN
data/minecraft-hosts
data/mvps.org
data/someonewhocares.org
data/tiuxo
data/yoyo.org
extensions/fakenews
extensions/gambling/bigdargon
extensions/gambling/sinfonietta
extensions/porn/bigdargon
extensions/porn/brijrajparmar27
extensions/porn/clefspeare13
extensions/porn/sinfonietta
extensions/porn/sinfonietta-snuff
extensions/social/sinfonietta
extensions/social/tiuxo
"

IFS='
'

for item in $lists; do
  echo "" > $item/stats.out

  for HASH_DATE in $(git log --reverse --format="%t,%as" -- $item);  do
    # echo $item $HASH_DATE
    IFS=" "
    split=(${HASH_DATE//,/ })
    domains=$(rh -q -m <(git show ${split[0]}:$item/hosts))
    echo  $item ${split[1]} ${domains}
    echo ${split[1]},${domains} >> ${item}/stats.out
    IFS='
'
  done
done
