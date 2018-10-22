#!/bin/bash
while read package
do
  echo $(date +'%F %T %z') ${package#/var/cache/apt/archives/} "(sudo user: ${SUDO_USER})" | logger -p "auth.notice" -t "dpkg-log"
done
