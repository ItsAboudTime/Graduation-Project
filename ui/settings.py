import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional

from cursor.config import (
    DEFAULT_SPEED_PX_PER_SEC,
    DEFAULT_FRAME_RATE,
    DEFAULT_SCROLL_SPEED_PX_PER_SEC,
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
        master.geometry("400x300")
        master.resizable(False, False)

        # Labels and input fields
        tk.Label(master, text="Cursor Speed (px/s):", font=("Arial", 12)).pack(pady=10)
        self.speed_var = tk.StringVar(value=str(DEFAULT_SPEED_PX_PER_SEC))
        speed_entry = tk.Entry(
            master, textvariable=self.speed_var, font=("Arial", 12), width=20
        )
        speed_entry.pack()

        tk.Label(master, text="Frame Rate (fps):", font=("Arial", 12)).pack(pady=10)
        self.frame_rate_var = tk.StringVar(value=str(DEFAULT_FRAME_RATE))
        frame_rate_entry = tk.Entry(
            master, textvariable=self.frame_rate_var, font=("Arial", 12), width=20
        )
        frame_rate_entry.pack()

        tk.Label(master, text="Scroll Speed (px/s):", font=("Arial", 12)).pack(
            pady=10
        )
        self.scroll_speed_var = tk.StringVar(
            value=str(DEFAULT_SCROLL_SPEED_PX_PER_SEC)
        )
        scroll_speed_entry = tk.Entry(
            master, textvariable=self.scroll_speed_var, font=("Arial", 12), width=20
        )
        scroll_speed_entry.pack()

        # Save button
        save_button = tk.Button(
            master,
            text="Save",
            font=("Arial", 14),
            bg="green",
            fg="white",
            command=self.save_config,
        )
        save_button.pack(pady=20)

    def save_config(self):
        try:
            speed = float(self.speed_var.get())
            frame_rate = int(self.frame_rate_var.get())
            scroll_speed = float(self.scroll_speed_var.get())

            if self.on_save:
                self.on_save(speed, frame_rate, scroll_speed)
                messagebox.showinfo("Success", "Configuration updated successfully!")
            else:
                # Fallback for standalone usage or testing
                messagebox.showinfo(
                    "Success",
                    f"Configuration updated:\n\n"
                    f"Speed: {speed} px/s\n"
                    f"Frame Rate: {frame_rate} fps\n"
                    f"Scroll Speed: {scroll_speed} px/s",
                )
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")


def main():
    root = tk.Tk()
    app = SettingsWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
