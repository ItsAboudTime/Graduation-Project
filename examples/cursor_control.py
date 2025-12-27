import sys
import threading
import tkinter as tk
import queue

from cursor import create_cursor
from ui.settings import SettingsWindow


def parse_coords(raw: str):
    """
    Parse user input like '800 400', '800,400' or 'q'.

    Returns:
      - (x, y) as ints
      - the string "quit" if the user entered 'q' (case-insensitive)
    Raises:
      - ValueError for invalid input
    """
    s = raw.strip()
    if s.lower() == "q":
        return "quit"

    s = s.replace(",", " ")
    parts = [p for p in s.split() if p]
    if len(parts) != 2:
        raise ValueError("Please enter two numbers like: 800 400 or 800,400")

    x = int(float(parts[0]))
    y = int(float(parts[1]))
    return x, y


def run_cli_loop(cur, stop_queue):
    """
    Runs the CLI blocking input loop in a background thread.
    Signals the main thread to stop via stop_queue.
    """
    minx, miny, maxx, maxy = cur.get_virtual_bounds()
    print("Cursor Move (CLI)")
    print(f"Virtual screen bounds: x [{minx}..{maxx}], y [{miny}..{maxy}]")
    print(f"Speed: {cur.speed_px_per_sec} px/s")
    print("Enter coordinates as 'x y' or 'x,y' (type 'q' to quit).")
    print("Commands: 'left' for left click, 'right' for right click, 'scroll <delta>' for scrolling.\n")

    while True:
        try:
            # This blocks, so it must live in a thread
            raw = input("Command > ")
        except KeyboardInterrupt:
            print("\nBye.")
            stop_queue.put("QUIT")
            break

        try:
            if raw.lower() == "q":
                print("Bye.")
                stop_queue.put("QUIT")
                break

            if raw.lower() == "left":
                print("Performing left click...")
                cur.left_click()
                continue

            if raw.lower() == "right":
                print("Performing right click...")
                cur.right_click()
                continue

            if raw.lower().startswith("scroll"):
                try:
                    parts = raw.split()
                    delta = int(parts[1])
                    print(f"Scrolling {'up' if delta > 0 else 'down'} by {delta}...")
                    cur.scroll_with_speed(delta)
                except (IndexError, ValueError):
                    print("Invalid scroll command. Use 'scroll <delta>' where delta is an integer.")
                continue

            result = parse_coords(raw)
            x, y = result
            print(f"Moving to ({x}, {y}) ...")
            cur.move_to_with_speed(x, y)
        except ValueError as e:
            print(e)


def main():
    cur = create_cursor()

    # 1. Initialize Tkinter in the MAIN thread
    try:
        root = tk.Tk()
    except Exception as e:
        print(f"Fatal Error: Could not start Tkinter: {e}")
        return

    # 2. Create a Queue for communication
    msg_queue = queue.Queue()

    # 3. Setup the Settings UI
    def on_save(speed: float, frame_rate: int, scroll_speed: float):
        try:
            cur.update_config(speed, frame_rate, scroll_speed)
            print(f"\nConfiguration updated: speed={speed}, fps={frame_rate}, scroll={scroll_speed}")
        except Exception as e:
            print(f"\nFailed to update cursor configuration: {e}")

    try:
        settings_win = SettingsWindow(root, on_save=on_save)
    except Exception as e:
        print(f"Warning: failed to init settings UI: {e}")

    # 4. Define the Queue Polling function (runs on Main Thread)
    def check_queue():
        try:
            # Check if the thread sent a message
            msg = msg_queue.get_nowait()
            if msg == "QUIT":
                root.quit()  # Break the mainloop
                sys.exit(0)
        except queue.Empty:
            pass
        
        # Schedule next check in 100ms
        root.after(100, check_queue)

    # 5. Start the CLI loop in a BACKGROUND thread
    # We pass 'cur' and 'msg_queue' to it
    t = threading.Thread(target=run_cli_loop, args=(cur, msg_queue), daemon=True)
    t.start()

    # 6. Start the Polling and the Mainloop
    check_queue()
    root.mainloop()


if __name__ == "__main__":
    sys.exit(main())