#!/bin/bash

if [ "$1" = "help" ]; then
    echo "Runs the qstat command on a specified server"
fi

if [ "$PBS_SERVER" = "" ]; then
    echo "To set up, add the following line to ~/.bash_profile:"
    echo "export PBS_SERVER=\"userid@hostname\""
    echo "(replacing userid with your user id and hostname with the name of your server)"
    exit 0
fi

CMD="qstat"
if [ "$1" = "jobs" ]; then
    CMD="n=\`qstat | wc -l\`; qstat | cut -b 1-16 | tail -\$(( n - 2 ))"
elif [ "$1" = "names" ]; then
    CMD="qstat | cut -b 19-34"
elif [ "$1" = "users" ]; then
    CMD="qstat | cut -b 36-51"
elif [ "$1" = "time" ]; then
    CMD="qstat | cut -b 54-61"
elif [ "$1" = "status" ]; then
    CMD="qstat | cut -b 63-63"
elif [ "$1" = "queue" ]; then
    CMD="qstat | cut -b 65-73"
fi

ssh $PBS_SERVER "$CMD"
