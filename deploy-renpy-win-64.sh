#!/bin/bash

# Activate fail-fast
set -e

if [ -z "$1" ] 
  then
    echo "Please specify the path (\$1) to copy renpy into."
    exit 0
fi

# Validate $1
mkdir $1
rmdir $1

# Activate the virtualenv
. tmp/virtualenv.py2/bin/activate

# Build for Windows 64-bit
./build.py --platform windows --arch x86_64

# Exit from virtualenv
deactivate

echo "Copying the renpy content to $1..."
# Copy the renpy content to $1 directory
cp -r ./renpy $1
# This folder is supposed to be named 'lib', not 'lib2'
mv /mnt/d/renpy-debug/lib2 $1/lib
