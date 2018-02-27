#!/bin/bash

# A simple script to archive directories

echo "Archiving $1"

tar -zvcf $1.tar.gz $1

echo "Done"
