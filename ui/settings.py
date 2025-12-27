import sys
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional

from cursor.constants import (
    DEFAULT_MOVE_PX_PER_SEC,
    DEFAULT_FRAME_RATE,
    DEFAULT_SCROLL_UNITS_PER_SEC,
)


class SettingsWindow:
    def __init__(
        self,
        master,
        on_save: Optional[Callable[[float, int, float], None]] = None,
    ):
        self.master = master
        self.on_save = on_save
        master.title("Cursor Configuration")
        master.geometry("400x320")
        master.resizable(False, False)

        # --- Move Speed ---
        tk.Label(master, text="Move Speed (px/s):", font=("Arial", 12)).pack(pady=(15, 5))
        self.move_speed_var = tk.StringVar(value=str(DEFAULT_MOVE_PX_PER_SEC))
        move_speed_entry = tk.Entry(
            master, textvariable=self.move_speed_var, font=("Arial", 12), width=20
        )
        move_speed_entry.pack()

        # --- Frame Rate ---
        tk.Label(master, text="Frame Rate (fps):", font=("Arial", 12)).pack(pady=(15, 5))
        self.frame_rate_var = tk.StringVar(value=str(DEFAULT_FRAME_RATE))
        frame_rate_entry = tk.Entry(
            master, textvariable=self.frame_rate_var, font=("Arial", 12), width=20
        )
        frame_rate_entry.pack()

        # --- Scroll Speed ---
        tk.Label(master, text="Scroll Speed (units/s):", font=("Arial", 12)).pack(pady=(15, 5))
        self.scroll_units_var = tk.StringVar(value=str(DEFAULT_SCROLL_UNITS_PER_SEC))
        scroll_speed_entry = tk.Entry(
            master, textvariable=self.scroll_units_var, font=("Arial", 12), width=20
        )
        scroll_speed_entry.pack()

        # --- Save Button ---
        save_button = tk.Button(
            master,
            text="Save",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self.save_config,
            padx=10,
            pady=5
        )
        save_button.pack(pady=25)

    def save_config(self):
        try:
            # Parse values
            move_speed = float(self.move_speed_var.get())
            frame_rate = int(self.frame_rate_var.get())
            scroll_units = float(self.scroll_units_var.get())

            # Validate basic logic (prevent negative speed or 0 FPS)
            if move_speed <= 0 or frame_rate <= 0 or scroll_units <= 0:
                 messagebox.showerror("Error", "Values must be greater than zero.")
                 return

            if self.on_save:
                self.on_save(move_speed, frame_rate, scroll_units)
                messagebox.showinfo("Success", "Configuration updated successfully!")
            else:
                # Fallback for standalone usage or testing
                messagebox.showinfo(
                    "Success",
                    f"Configuration updated:\n\n"
                    f"Move Speed: {move_speed} px/s\n"
                    f"Frame Rate: {frame_rate} fps\n"
                    f"Scroll Speed: {scroll_units} units/s",
                )
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")


def main():
    root = tk.Tk()
    # root.eval('tk::PlaceWindow . center')
    app = SettingsWindow(root)
    root.mainloop()


if __name__ == "__main__":
    sys.exit(main())
