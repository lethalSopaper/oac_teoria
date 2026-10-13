# MicroPython Pico 2 W Practice

This project contains MicroPython practices for the Raspberry Pi Pico 2 W.
The `upload.sh` script uploads and runs any selected MicroPython file.

## Requirements

- Raspberry Pi Pico 2 W
- MicroPython ARM firmware for `RPI_PICO2_W`
- Python 3
- `mpremote`

Do not use the RISC-V firmware if the program uses `micropython.asm_thumb`.

Install `mpremote` with:

```bash
python3 -m pip install --user mpremote
```

## First firmware installation

1. Download the latest regular `.uf2` firmware from the [Pico 2 W MicroPython downloads](https://micropython.org/download/RPI_PICO2_W/).
2. Hold `BOOTSEL` while connecting the Pico 2 W to USB.
3. Copy the firmware to the mounted `RP2350` drive:

    ```bash
    cp RPI_PICO2_W-*.uf2 /run/media/$USER/RP2350/
    ```

After the board restarts, verify its serial device:

```bash
ls /dev/ttyACM*
```

## Upload and run a practice

Make the helper executable once:

```bash
chmod +x upload.sh
```

Then provide the Python file to upload:

```bash
./upload.sh practica_01.py
```

The helper:

1. Uploads the selected file to the board as `main.py`.
2. Runs the selected file and displays its output.
3. Ensures the selected file runs automatically after reset or power-up.

For another practice, use the same command with its filename:

```bash
./upload.sh practica_08.py
```

The default serial device is `/dev/ttyACM0`. To specify another device:

```bash
./upload.sh practica_08.py /dev/ttyACM1
```

## Graficar la práctica 02

La práctica 02 envía cada muestra con el formato
`DATA,tiempo_ms,entrada,salida`. Para visualizarla en tiempo real, carga el
firmware y termina la sesión de `mpremote` con `Ctrl+C`:

```bash
cd practica_02
../upload.sh source/practica_02.py /dev/ttyACM0
```

Después abre la interfaz en otra terminal:

```bash
python3 graficar_practica_02.py /dev/ttyACM0
```

También se puede automatizar la copia del firmware, el reinicio de la Pico y
la apertura de la interfaz con un solo comando:

```bash
cd practica_02
./ejecutar_practica_02.sh
```

Para utilizar otro puerto:

```bash
./ejecutar_practica_02.sh /dev/ttyACM1
```

Antes de ejecutarlo se debe cerrar Thonny y cualquier otro programa que esté
usando el puerto serial.

La ventana permite conectar y desconectar el puerto, pausar la gráfica,
limpiar las muestras y guardar los datos recibidos como CSV. Requiere
`pyserial` y Tkinter; en Linux se pueden instalar con:

```bash
python3 -m pip install pyserial
```

## Current practice

`practica_01.py` compares an ARM Thumb assembly implementation and a pure
MicroPython implementation of the integer square root using binary search.
