#!/usr/bin/env python3
"""Monitor en tiempo real para el sistema de control de la practica 02."""

import argparse
import csv
import queue
import re
import threading
import time
import tkinter as tk
from collections import deque
from tkinter import filedialog, messagebox, ttk

import serial
from serial.tools import list_ports


DATA_PATTERN = re.compile(
    r"DATA\s*,\s*([-+]?\d+(?:\.\d+)?)\s*,\s*"
    r"([-+]?\d+(?:\.\d+)?)\s*,\s*([-+]?\d+(?:\.\d+)?)"
)
LEGACY_PATTERN = re.compile(
    r"x\[k\]\s*:\s*([-+]?\d+(?:\.\d+)?)\s*\|\s*"
    r"y\[k\]\s*:\s*([-+]?\d+(?:\.\d+)?)"
)


class Monitor:
    def __init__(self, root, initial_port=None):
        self.root = root
        self.root.title("Practica 02 | Monitor de control")
        self.root.geometry("980x700")
        self.root.minsize(760, 520)

        self.serial_port = None
        self.reader_thread = None
        self.stop_reader = threading.Event()
        self.samples = deque(maxlen=1200)
        self.incoming = queue.Queue()
        self.paused = False
        self.fallback_time = 0.0
        self.first_device_time = None

        self.port_var = tk.StringVar(value=initial_port or self.detect_port())
        self.status_var = tk.StringVar(value="Desconectado")
        self.count_var = tk.StringVar(value="Muestras: 0")

        self.build_controls()
        self.build_plot()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.refresh_plot()
        if self.port_var.get():
            self.root.after(150, self.auto_connect)

    @staticmethod
    def detect_port():
        ports = [port.device for port in list_ports.comports()]
        return ports[0] if ports else "/dev/ttyACM0"

    def build_controls(self):
        controls = ttk.Frame(self.root, padding=(10, 8))
        controls.pack(fill=tk.X)

        ttk.Label(controls, text="Puerto:").pack(side=tk.LEFT)
        self.port_combo = ttk.Combobox(
            controls, textvariable=self.port_var, width=18
        )
        self.port_combo.pack(side=tk.LEFT, padx=(5, 8))
        ttk.Button(controls, text="Actualizar", command=self.refresh_ports).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        self.connect_button = ttk.Button(
            controls, text="Conectar", command=self.toggle_connection
        )
        self.connect_button.pack(side=tk.LEFT)
        ttk.Button(controls, text="Pausar", command=self.toggle_pause).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(controls, text="Limpiar", command=self.clear_samples).pack(
            side=tk.LEFT
        )
        ttk.Button(controls, text="Guardar CSV", command=self.save_csv).pack(
            side=tk.LEFT, padx=5
        )

        ttk.Label(controls, textvariable=self.count_var).pack(side=tk.RIGHT)
        ttk.Label(self.root, textvariable=self.status_var, padding=(10, 0)).pack(
            anchor=tk.W
        )

    def build_plot(self):
        self.canvas = tk.Canvas(
            self.root, background="#ffffff", highlightthickness=1,
            highlightbackground="#c8c8c8"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        self.canvas.bind("<Configure>", lambda event: self.update_lines())

    def refresh_ports(self):
        ports = [port.device for port in list_ports.comports()]
        self.port_combo["values"] = ports
        if ports and self.port_var.get() not in ports:
            self.port_var.set(ports[0])
        self.status_var.set(
            "Puertos actualizados" if ports else "No se encontraron puertos seriales"
        )

    def toggle_connection(self):
        if self.serial_port is None:
            self.connect()
        else:
            self.disconnect()

    def auto_connect(self):
        if self.serial_port is not None:
            return
        if self.connect(show_errors=False):
            return
        self.status_var.set("Esperando el puerto serial...")
        self.root.after(500, self.auto_connect)

    def connect(self, show_errors=True):
        port = self.port_var.get().strip()
        if not port:
            if show_errors:
                messagebox.showerror("Puerto serial", "Selecciona un puerto de la Pico.")
            return False
        try:
            self.serial_port = serial.Serial(port, 115200, timeout=0.2)
        except serial.SerialException as error:
            self.serial_port = None
            if show_errors:
                messagebox.showerror("No se pudo conectar", str(error))
            return False

        self.stop_reader.clear()
        self.reader_thread = threading.Thread(target=self.read_serial, daemon=True)
        self.reader_thread.start()
        self.connect_button.configure(text="Desconectar")
        self.status_var.set(f"Conectado a {port} | esperando muestras")
        return True

    def disconnect(self):
        self.stop_reader.set()
        if self.serial_port is not None:
            self.serial_port.close()
        self.serial_port = None
        self.connect_button.configure(text="Conectar")
        self.status_var.set("Desconectado")

    def read_serial(self):
        while not self.stop_reader.is_set() and self.serial_port is not None:
            try:
                line = self.serial_port.readline().decode("utf-8", errors="ignore")
            except (serial.SerialException, OSError):
                break
            if line:
                sample = self.parse_sample(line)
                if sample is not None:
                    self.incoming.put(sample)

    def parse_sample(self, line):
        match = DATA_PATTERN.search(line)
        if match:
            device_time, input_value, output_value = map(float, match.groups())
            if self.first_device_time is None:
                self.first_device_time = device_time
            elapsed = (device_time - self.first_device_time) / 1000.0
            return elapsed, input_value, output_value

        # Permite usar versiones anteriores del firmware que imprimen x[k] e y[k].
        match = LEGACY_PATTERN.search(line)
        if match:
            input_value, output_value = map(float, match.groups())
            self.fallback_time += 0.025
            return self.fallback_time, input_value, output_value
        return None

    def toggle_pause(self):
        self.paused = not self.paused
        self.status_var.set("Gráfica pausada" if self.paused else "Gráfica activa")

    def clear_samples(self):
        self.samples.clear()
        self.first_device_time = None
        self.fallback_time = 0.0
        self.update_lines()
        self.count_var.set("Muestras: 0")

    def refresh_plot(self):
        while True:
            try:
                sample = self.incoming.get_nowait()
            except queue.Empty:
                break
            if not self.paused:
                self.samples.append(sample)

        if not self.paused:
            self.update_lines()
        self.root.after(50, self.refresh_plot)

    def update_lines(self):
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 500)
        height = max(self.canvas.winfo_height(), 400)
        samples = list(self.samples)
        self.draw_panel(
            0, 0, width, height // 2, samples, 1, "Entrada x[k]", "#1769aa"
        )
        self.draw_panel(
            0, height // 2, width, height, samples, 2, "Salida y[k]", "#d1495b"
        )
        self.count_var.set(f"Muestras: {len(self.samples)}")

    def draw_panel(self, left, top, right, bottom, samples, value_index, title, color):
        margin_left, margin_top = 72, 28
        margin_right, margin_bottom = 20, 30
        plot_left = left + margin_left
        plot_top = top + margin_top
        plot_right = right - margin_right
        plot_bottom = bottom - margin_bottom
        self.canvas.create_text(
            plot_left, top + 10, text=title, anchor=tk.W,
            font=("TkDefaultFont", 10, "bold")
        )
        self.canvas.create_rectangle(plot_left, plot_top, plot_right, plot_bottom, outline="#aaaaaa")
        for fraction in (0.0, 0.5, 1.0):
            y = plot_bottom - fraction * (plot_bottom - plot_top)
            self.canvas.create_line(plot_left, y, plot_right, y, fill="#e5e5e5")

        if not samples or plot_right <= plot_left or plot_bottom <= plot_top:
            return
        times = [sample[0] for sample in samples]
        values = [sample[value_index] for sample in samples]
        right_time = max(30.0, times[-1])
        left_time = max(0.0, right_time - 30.0)
        maximum = max(1.0, max(values) * 1.1)

        points = []
        time_span = max(1.0, right_time - left_time)
        height_span = plot_bottom - plot_top
        for sample_time, value in zip(times, values):
            x = plot_left + (sample_time - left_time) / time_span * (plot_right - plot_left)
            y = plot_bottom - (value / maximum) * height_span
            points.extend((x, y))
        if len(points) >= 4:
            self.canvas.create_line(*points, fill=color, width=2, smooth=False)
        self.canvas.create_text(plot_left - 8, plot_top, text=f"{maximum:.0f}", anchor=tk.E)
        self.canvas.create_text(plot_left - 8, plot_bottom, text="0", anchor=tk.E)
        self.canvas.create_text(plot_right, bottom - 8, text=f"{right_time:.1f} s", anchor=tk.E)

    def save_csv(self):
        if not self.samples:
            messagebox.showinfo("Guardar CSV", "Todavía no hay muestras para guardar.")
            return
        filename = filedialog.asksaveasfilename(
            title="Guardar muestras",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos los archivos", "*.*")],
        )
        if not filename:
            return
        with open(filename, "w", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            writer.writerow(("tiempo_s", "entrada_x_k", "salida_y_k"))
            writer.writerows(self.samples)
        self.status_var.set(f"Datos guardados en {filename}")

    def close(self):
        self.disconnect()
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", nargs="?", help="Puerto serial, por ejemplo /dev/ttyACM0")
    args = parser.parse_args()
    root = tk.Tk()
    Monitor(root, args.port)
    root.mainloop()


if __name__ == "__main__":
    main()
