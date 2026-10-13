#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
firmware="$script_dir/source/practica_02.py"
monitor="$script_dir/graficar_practica_02.py"
device="${1:-/dev/ttyACM0}"

if [[ ! -f "$firmware" ]]; then
    echo "No se encontró el firmware: $firmware" >&2
    exit 1
fi

if [[ ! -f "$monitor" ]]; then
    echo "No se encontró el monitor: $monitor" >&2
    exit 1
fi

if [[ ! -e "$device" ]]; then
    echo "No se encontró el puerto serial: $device" >&2
    echo "Conecta la Pico y vuelve a intentarlo." >&2
    exit 1
fi

if fuser "$device" >/dev/null 2>&1; then
    echo "Cerrando el proceso que está usando $device..."
    fuser -k "$device" >/dev/null 2>&1 || true
fi

echo "Copiando el firmware a la Raspberry Pi Pico 2 W..."
mpremote connect "$device" fs cp "$firmware" :main.py

echo "Reiniciando la Pico para aplicar los coeficientes actuales..."
mpremote connect "$device" soft-reset

echo "Esperando a que reaparezca el puerto serial..."
for attempt in {1..10}; do
    if [[ -e "$device" ]]; then
        break
    fi
    if command -v udevadm >/dev/null 2>&1; then
        udevadm settle --timeout=1 >/dev/null 2>&1 || true
    fi
done

if [[ ! -e "$device" ]]; then
    echo "La Pico no volvió a aparecer como $device después del reinicio." >&2
    echo "Desconecta y conecta nuevamente la Pico, y vuelve a ejecutar este script." >&2
    exit 1
fi

echo "Abriendo la interfaz gráfica en $device"
exec python3 "$monitor" "$device"
