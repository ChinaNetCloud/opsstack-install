#!/bin/bash

echo "Symlinking executable to /usr/bin"
ln -s <%= prefix %>/opsstack-configure.sh /usr/bin/opsstack-configure
