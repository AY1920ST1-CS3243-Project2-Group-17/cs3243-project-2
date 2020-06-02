#!/bin/bash

for layout in $(ls layouts | sed -e 's/\.lay$//')
do
    echo "Testing $layout..."
    python pacman.py -p ApproximateQAgent -a extractor=SimpleExtractor -x 50 -n 60 -l $layout
    printf "\n"
done

