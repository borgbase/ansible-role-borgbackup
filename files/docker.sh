#!/usr/bin/env bash

# Purpose: Get and save state of docker containers and stop them for a backup
# Author: Frank Dornheim <dornheim@posteo.de> under GPLv2+
# Category: Core
# Override: False

FILENAME=/tmp/borgbackup_docker.state
DOCKERGROUP=docker

#
# Checks the state of a Docker container and saves it. 
# Running containers are stopped to maintain a consistent backup.
# After the backup finished, in a second step, all containers are restarted.
#

# Check for permissions to work with docker
if [[ $(id -u) -ne 0 ]] || [[ $(groups) =~ '$DOCKERGROUP' ]]; then
  echo "Please run as root or member of group docker"
  exit 1
fi

function rwo(){ tr ' ' '\n'<<<"$@"|tac|tr '\n' ' ';} # reverse name order

case "$1" in
  start)
    if [[ ! -f "$FILENAME" ]]; then
      echo "$FILENAME didnt loger exist so cat restart container."
      exit 1
    fi

    container_list=$(cat "$FILENAME")

    echo "Containers were stopped in the following order: $container_list"
    container_start_list=$(rwo $container_list)
    echo "Reversed start order: $container_start_list"

    for i in $container_start_list; do
      echo "Start container: $i"
      docker start $i &>/dev/null
    done

    #clean up
    rm $FILENAME
    ;;

  stop)
    # delete old state file
    if [[ -f "$FILENAME" ]]; then
      rm "$FILENAME"
    fi
    
    # Named container or all container
    if [[ $# -gt 1 ]]; then
      container_list="${@:2:$#}" # Slice Arguments the first is {start|stop} the other are container names
    else
      # No container names passed, this means all containers are analyzed
      container_list=$( docker inspect --format={{.Name}} $( docker ps -aq --no-trunc ) | cut -c2- )
    fi

    # save state and shutdown active container
    for i in $container_list; do
      state=$( docker ps -a -f name=$i | grep $i 2> /dev/null | awk '{ print $7 }')
      if [[ $state -eq Up ]]; then
        echo "Stop container: $i"
        docker stop $i &>/dev/null
      else
        echo "The State of container: $i is not up, so ignoring them."
      fi
    done
    echo "Containers were stopped in the following order: $( echo $container_list | tr '\n' ' ')"
    echo $container_list > $FILENAME
    ;;

  --help)
    echo "$0 {start|stop} <CONTAINERNAME> <CONTAINERNAME 2>"
    echo ""
    echo "stop:  Save the status of all running container an stop them due backup."
    echo "start: Load status of container before the backup and start them."
    echo "<CONTAINERNAME>: start|stop of a named container"
    echo ""
    ;;

  *)
    echo "Usage: $0. The first argument have to be:{start|stop}. See --help." >&2
    exit 1
    ;;
esac
