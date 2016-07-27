#!/bin/bash

echo "Symlinking executable to /usr/bin"
ln -s <%= prefix %>/nc-configure.py /usr/bin/nc-configure
