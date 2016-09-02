#!/usr/bin/env bash

if [ "${1:-0}" -gt 0 ]; then
    exit 0
fi

if [ \( -L "/usr/bin/opsstack-install" \) ]; then
    echo "Uninstalling executables 1/2"
    unlink /usr/bin/opsstack-install
fi
if [ \( -L "/var/lib/opsstack/common/env/bin/opsstack-install" \) ]; then
    echo "Uninstalling executables 2/2"
    unlink /var/lib/opsstack/common/env/bin/opsstack-install
fi
