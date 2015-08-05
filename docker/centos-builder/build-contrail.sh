#!/bin/bash

for i in "$@"; do
    case $i in
	-j*)
            NJOBS=$i
	    ;;
	*)
	    ;;
    esac
done

cd /src/contrail
repo sync
export USER=nobody
scons $NJOBS --optimization=production install --root=/mnt/output
