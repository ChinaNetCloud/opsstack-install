#!/usr/bin/env bash

echo "Unlinking executable from /usr/bin if it was there already"
unlink /usr/bin/nc-configure
