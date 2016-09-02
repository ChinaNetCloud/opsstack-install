#!/usr/bin/env bash

if [ ! \( -L "/var/lib/opsstack/common/env/bin/opsstack-install" \) ]; then
    echo "Installing executables 1/2"
    ln -s /var/lib/opsstack/configure/opsstack-install.py /var/lib/opsstack/common/env/bin/opsstack-install
fi
if [ ! \( -L "/usr/bin/opsstack-install" \) ]; then
    echo "Installing executables 2/2"
    ln -s /var/lib/opsstack/configure/opsstack-install.sh /usr/bin/opsstack-install
fi
