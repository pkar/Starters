#!/bin/bash

command -v coffee >/dev/null 2>&1 || { echo "I require node/coffee but it's not installed. Abort baby." >&2; exit 1; }

coffee --watch --lint --compile .

