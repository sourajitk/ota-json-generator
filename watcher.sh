#!/bin/bash

TARGET=~/12-OFFICIAL/

inotifywait -m -e moved_to --format "%w%f" -r $TARGET \
    | while read PATHNAME
        do
            filename="${PATHNAME##*/}"
            if [[ $filename == statix_*-OFFICIAL.zip ]];
            then
                echo "Detected $PATHNAME, generating json..."
                stripped="${PATHNAME#*_}"
                DEVICE="${stripped%%-*}"
                python3 gen_json.py $PATHNAME $DEVICE > ~/json/$DEVICE.json
            else
                echo "$PATHNAME isn't an OTA update, skipping..."
            fi
        done
