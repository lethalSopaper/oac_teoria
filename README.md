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

## Current practice

`practica_01.py` compares an ARM Thumb assembly implementation and a pure
MicroPython implementation of the integer square root using binary search.
