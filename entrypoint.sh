#!/bin/sh

# Check for BILLML_RUN_FOR_EVER env variable.
if [ $BILLML_RUN_FOR_EVER = "True" ]
    then
        tail -f /dev/null

elif [  $BILLML_RUN_FOR_EVER = "False" ]
    then
        echo "TODO: run logic here."
fi
