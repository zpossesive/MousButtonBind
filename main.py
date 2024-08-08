import tkinter as tk
import customtkinter as ctk
from pynput import mouse, keyboard
from threading import Thread
import pystray
from PIL import Image, ImageDraw
import json
import sys
import os

class KeyReplacerApp:
    CONFIG_FILE = os.path.join(os.getenv('APPDATA'), 'key_replacer_config.json')

    def __init__(self, root):
        self.root = root
        self.root.title("MB Key Switcher")

        self.load_config()

        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(padx=20, pady=20)

        self.label1 = ctk.CTkLabel(self.frame, text="Button for the front side button:")
        self.label1.grid(row=0, column=0, padx=10, pady=5)
        self.key1_entry = ctk.CTkEntry(self.frame)
        self.key1_entry.grid(row=0, column=1, padx=10, pady=5)
        self.key1_entry.insert(0, self.key1)
a
        self.label2 = ctk.CTkLabel(self.frame, text="Button for the rear side button:")
        self.label2.grid(row=1, column=0, padx=10, pady=5)
        self.key2_entry = ctk.CTkEntry(self.frame)
        self.key2_entry.grid(row=1, column=1, padx=10, pady=5)
        self.key2_entry.insert(0, self.key2)

        self.start_button = ctk.CTkButton(self.frame, text="Start", command=self.start_replacing)
        self.start_button.grid(row=2, columnspan=2, pady=10)

        self.stop_button = ctk.CTkButton(self.frame, text="Stop", command=self.stop_replacing)
        self.stop_button.grid(row=3, columnspan=2, pady=10)

        self.minimize_button = ctk.CTkButton(self.frame, text="Hide", command=self.minimize_to_tray)
        self.minimize_button.grid(row=4, columnspan=2, pady=10)

        self.stop_thread = False

    def start_replacing(self):
        self.key1 = self.key1_entry.get()
        self.key2 = self.key2_entry.get()

        self.save_config()

        self.stop_thread = False
        self.listener_thread = Thread(target=self.run_mouse_listener)
        self.listener_thread.start()

    def stop_replacing(self):
        self.stop_thread = True
        self.listener_thread.join()

    def run_mouse_listener(self):
        keyboard_controller = keyboard.Controller()

        def on_click(x, y, button, pressed):
            if self.stop_thread:
                return False

            if pressed:
                if button == mouse.Button.x2:
                    keyboard_controller.press(self.key1)
                    keyboard_controller.release(self.key1)
                elif button == mouse.Button.x1:
                    keyboard_controller.press(self.key2)
                    keyboard_controller.release(self.key2)

        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    def minimize_to_tray(self):
        self.root.withdraw() 
        self.tray_icon = pystray.Icon("name", self.create_image(), "Key Replacer", self.create_menu())
        self.tray_icon.run()

    def create_image(self):
        image = Image.new('RGB', (16, 16), color=(0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.polygon([(8, 4), (12, 8), (8, 12), (4, 8)], fill=(255, 0, 0))  
        dc.polygon([(8, 4), (10, 2), (8, 0), (6, 2)], fill=(255, 0, 0)) 
        dc.point((7, 3), fill=(255, 255, 255))
        dc.point((9, 3), fill=(255, 255, 255)) 
        return image

    def create_menu(self):
        menu = pystray.Menu(
            pystray.MenuItem("Open", self.show_window),
            pystray.MenuItem("Close", self.quit_application)
        )
        return menu

    def show_window(self, icon, item):
        self.root.deiconify()  
        icon.stop()  

    def quit_application(self, icon, item):
        self.stop_replacing()  
        icon.stop()  
        sys.exit() 
    def save_config(self):
        config = {
            'key1': self.key1,
            'key2': self.key2
        }
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.key1 = config.get('key1', '-')
                self.key2 = config.get('key2', '=')
        else:
            self.key1 = '-'
            self.key2 = '='

root = ctk.CTk()
app = KeyReplacerApp(root)
root.mainloop()
