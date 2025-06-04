import tkinter as tk
from tkinter import ttk
import pyautogui
import cv2
import numpy as np
import time
import keyboard
import win32gui
import threading
import mss
import os

class GreySquareClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Colouring Game 3 Auto-Clicker")
        self.root.geometry("420x350")
        self.is_running = False
        self.max_number = tk.IntVar(value=30)
        self.delay_var = tk.DoubleVar(value=0.01)
        self.create_widgets()
        keyboard.add_hotkey('f6', self.hotkey_start)
        keyboard.add_hotkey('f7', self.hotkey_stop)

    def create_widgets(self):
        window_frame = ttk.LabelFrame(self.root, text="Window Selection", padding=10)
        window_frame.pack(fill="x", padx=10, pady=5)
        self.window_list = ttk.Combobox(window_frame, state="readonly")
        self.window_list.pack(fill="x", pady=5)
        self.update_window_list()
        ttk.Button(window_frame, text="Refresh Windows", command=self.update_window_list).pack(fill="x", pady=5)

        monitor_frame = ttk.LabelFrame(self.root, text="Monitor Selection", padding=10)
        monitor_frame.pack(fill="x", padx=10, pady=5)
        self.monitor_var = tk.IntVar(value=1)
        self.monitor_list = ttk.Combobox(monitor_frame, state="readonly")
        self.monitor_list.pack(fill="x", pady=5)
        self.update_monitor_list()
        ttk.Button(monitor_frame, text="Refresh Monitors", command=self.update_monitor_list).pack(fill="x", pady=5)

        settings_frame = ttk.LabelFrame(self.root, text="Settings", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(settings_frame, text="Click Delay (seconds, e.g. 0.01):").pack(fill="x")
        ttk.Entry(settings_frame, textvariable=self.delay_var).pack(fill="x", pady=5)

        control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        self.start_btn = ttk.Button(control_frame, text="Start F6", command=self.start_clicking)
        self.start_btn.pack(fill="x", pady=5)
        self.stop_btn = ttk.Button(control_frame, text="Stop F7", command=self.stop_clicking, state="disabled")
        self.stop_btn.pack(fill="x", pady=5)

        status_frame = ttk.LabelFrame(self.root, text="Status", padding=10)
        status_frame.pack(fill="x", padx=10, pady=5)
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(fill="x", pady=5)

    def update_window_list(self):
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows.append((title, hwnd))
            return True
        windows = []
        win32gui.EnumWindows(callback, windows)
        self.window_list['values'] = [w[0] for w in windows]

    def update_monitor_list(self):
        with mss.mss() as sct:
            monitors = sct.monitors
            monitor_names = [f"Monitor {i}: {m['left']},{m['top']} {m['width']}x{m['height']}" for i, m in enumerate(monitors) if i > 0]
            print("[DEBUG] Available monitors:")
            for i, m in enumerate(monitors):
                print(f"  Monitor {i}: {m}")
            self.monitor_list['values'] = monitor_names
            if monitor_names:
                self.monitor_list.current(0)
                self.monitor_var.set(1)

    def get_selected_monitor(self):
        idx = self.monitor_list.current() + 1  # mss uses 1-based index
        with mss.mss() as sct:
            if 1 <= idx < len(sct.monitors):
                return sct.monitors[idx]
            else:
                return sct.monitors[1]

    def start_clicking(self):
        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="Running...")
        threading.Thread(target=self.click_all_boxes, daemon=True).start()

    def click_all_boxes(self):
        debug_dir = 'debug_boxes'
        os.makedirs(debug_dir, exist_ok=True)
        left, top, width, height = 232, 65, 1499, 958  # corrected crop
        skipped = 0
        clicked = 0
        last_screenshot_time = 0
        cropped = None
        gray = None
        monitor = None
        import time as _time
        for y in range(0, height, 10):
            for x in range(0, width, 10):
                if not self.is_running:
                    print("[DEBUG] Stopped by user.")
                    self.status_label.config(text="Stopped")
                    self.start_btn.config(state="normal")
                    self.stop_btn.config(state="disabled")
                    return
                now = _time.time()
                if (cropped is None) or (now - last_screenshot_time > 2):
                    with mss.mss() as sct:
                        monitor = self.get_selected_monitor()
                        mss_img = sct.grab(monitor)
                        img = np.array(mss_img)
                        img_bgr = img[..., :3]
                        cropped = img_bgr[top:top+height, left:left+width]
                        if y == 0 and x == 0:
                            crop_path = os.path.join(debug_dir, 'cropped_game.png')
                            cv2.imwrite(crop_path, cropped)
                            print(f"[DEBUG] Saved cropped game window to {crop_path}")
                        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                        last_screenshot_time = now
                roi = gray[y:y+10, x:x+10]
                if roi.shape != (10, 10):
                    continue
                stddev = np.std(roi)
                if stddev < 30:
                    skipped += 1
                    continue  # likely filled (solid color)
                click_x = monitor['left'] + left + x + 5
                click_y = monitor['top'] + top + y + 5
                pyautogui.click(click_x, click_y, button='right')
                if self.delay_var.get() > 0:
                    time.sleep(self.delay_var.get())
                pyautogui.click(click_x, click_y, button='left')
                if self.delay_var.get() > 0:
                    time.sleep(self.delay_var.get())
                clicked += 1
        print(f"[DEBUG] Clicked {clicked} boxes, skipped {skipped} filled boxes.")
        self.status_label.config(text=f"Done! Clicked {clicked}, skipped {skipped}.")
        self.stop_clicking()

    def stop_clicking(self):
        self.is_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Stopped")

    def hotkey_start(self):
        if not self.is_running:
            self.start_clicking()

    def hotkey_stop(self):
        if self.is_running:
            self.stop_clicking()

def main():
    root = tk.Tk()
    app = GreySquareClicker(root)
    root.mainloop()

if __name__ == "__main__":
    main() 