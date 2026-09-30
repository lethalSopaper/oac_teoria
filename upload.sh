#!/usr/bin/env bash

set -euo pipefail

script="${1:?Usage: ./upload.sh SCRIPT.py [DEVICE]}"
device="${2:-/dev/ttyACM0}"

if [[ ! -f "$script" ]]; then
	echo "File not found: $script" >&2
	exit 1
fi

mpremote connect "$device" fs cp "$script" :main.py
mpremote connect "$device" run "$script"