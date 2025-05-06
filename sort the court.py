import pymem
from pymem.process import module_from_name
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Get the directory of the executable or script
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle (compiled with PyInstaller)
    application_path = os.path.dirname(sys.executable)
else:
    # If the application is run as a script
    application_path = os.path.dirname(os.path.abspath(__file__))


class SortTheCourtCheat:
    def __init__(self, root):
        self.root = root
        self.root.title("Sort The Court Cheat")
        self.root.geometry("400x350")
        self.root.resizable(False, False)

        # Configure style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50")
        self.style.configure("TFrame", background="#f0f0f0")

        # Initialize variables
        self.writing_enabled = False
        self.stop_writing_event = threading.Event()
        self.pm = None
        self.game_module = None
        self.ptrs = None
        self.writing_thread = None
        self.status_var = tk.StringVar(value="Status: Not connected")
        self.gold_var = tk.IntVar(value=9999)
        self.happiness_var = tk.IntVar(value=9999)
        self.population_var = tk.IntVar(value=9999)
        self.custom_values_enabled = tk.BooleanVar(value=False)

        # Store spinboxes for easy access later
        self.spinboxes = []

        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create title
        title_label = ttk.Label(
            main_frame,
            text="Sort The Court Cheat Tool",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=10)

        # Create connection button
        self.connect_button = ttk.Button(
            main_frame,
            text="Connect to Game",
            command=self.connect_to_game
        )
        self.connect_button.pack(fill="x", pady=5)

        # Create status label
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(pady=5)

        # Create separator
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill="x", pady=10)

        # Create custom values frame
        values_frame = ttk.Frame(main_frame)
        values_frame.pack(fill="x", pady=5)

        # Custom values checkbox
        custom_values_check = ttk.Checkbutton(
            values_frame,
            text="Enable Custom Values",
            variable=self.custom_values_enabled,
            command=self.toggle_custom_values
        )
        custom_values_check.pack(anchor="w")

        # Create value controls
        self.create_value_control(values_frame, "Gold:", self.gold_var)
        self.create_value_control(values_frame, "Happiness:", self.happiness_var)
        self.create_value_control(values_frame, "Population:", self.population_var)

        # Create toggle button
        self.toggle_button = ttk.Button(
            main_frame,
            text="Start Cheats",
            command=self.toggle_writing,
            state="disabled"
        )
        self.toggle_button.pack(fill="x", pady=10)

        # Create footer with credits
        footer_label = ttk.Label(
            main_frame,
            text="Game link: https://graebor.itch.io/sort-the-court",
            font=("Helvetica", 8)
        )
        footer_label.pack(side="bottom", pady=5)

        # Set up protocol for closing the window
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_value_control(self, parent, label_text, variable):
        """Create a labeled spinbox for value control"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=2)

        label = ttk.Label(frame, text=label_text, width=10)
        label.pack(side="left")

        spinbox = ttk.Spinbox(
            frame,
            from_=0,
            to=999999,
            textvariable=variable,
            width=10,
            state="disabled"
        )
        spinbox.pack(side="left", padx=5)

        self.spinboxes.append(spinbox)

        return spinbox

    def toggle_custom_values(self):
        """Enable or disable custom value inputs"""
        state = "normal" if self.custom_values_enabled.get() else "disabled"

        for spinbox in self.spinboxes:
            spinbox.configure(state=state)

    def connect_to_game(self):
        """Connect to the game process"""
        try:
            self.pm = pymem.Pymem("SortTheCourt.exe")
            self.game_module = module_from_name(self.pm.process_handle, "mono.dll").lpBaseOfDll
            self.ptrs = self.get_ptrs()

            self.status_var.set("Status: Connected")
            self.connect_button.configure(text="Reconnect", state="normal")
            self.toggle_button.configure(state="normal")

            # Start the writing thread
            if self.writing_thread is None or not self.writing_thread.is_alive():
                self.stop_writing_event.clear()
                self.writing_thread = threading.Thread(target=self.infinite_write)
                self.writing_thread.daemon = True
                self.writing_thread.start()

        except pymem.exception.ProcessNotFound:
            messagebox.showerror("Error", "Could not find process: Game not open or installed")
            self.status_var.set("Status: Game not found")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
            self.status_var.set(f"Status: Error - {e}")

    def get_ptr_addr(self, base, offsets):
        """Get pointer address from base and offsets"""
        addr = self.pm.read_int(base)
        for offset in offsets[:-1]:
            addr = self.pm.read_int(addr + offset)
        return addr + offsets[-1]

    def get_ptrs(self):
        """Get all game pointers"""
        gold_ptr = self.get_ptr_addr(self.game_module + 0x001F30AC, [0x3C4, 0x68, 0x38, 0x5C, 0x70, 0xB0, 0x0C])
        happiness_ptr = self.get_ptr_addr(self.game_module + 0x001F30AC, [0x548, 0x56C, 0x0C, 0x14, 0xD0, 0xB4, 0x0C])
        population_ptr = self.get_ptr_addr(self.game_module + 0x001F30AC, [0x548, 0x2C, 0x08, 0x56C, 0xD0, 0xB8, 0x0C])

        return {
            "Gold": gold_ptr,
            "Happiness": happiness_ptr,
            "Population": population_ptr
        }

    def infinite_write(self):
        """Write values in a loop"""
        while not self.stop_writing_event.is_set():
            if self.writing_enabled:
                try:
                    # Get current values if using custom values
                    gold_value = self.gold_var.get() if self.custom_values_enabled.get() else 9999
                    happiness_value = self.happiness_var.get() if self.custom_values_enabled.get() else 9999
                    population_value = self.population_var.get() if self.custom_values_enabled.get() else 9999

                    # Write values to memory
                    self.pm.write_int(self.ptrs["Gold"], gold_value)
                    self.pm.write_int(self.ptrs["Happiness"], happiness_value)
                    self.pm.write_int(self.ptrs["Population"], population_value)

                except pymem.exception.MemoryWriteError:
                    self.status_var.set("Status: Game closed")
                    self.writing_enabled = False
                    self.toggle_button.configure(text="Start Cheats")
                    return
                except Exception as e:
                    self.status_var.set(f"Status: Error - {e}")
                    self.writing_enabled = False
                    self.toggle_button.configure(text="Start Cheats")
                    return
            time.sleep(0.1)

    def toggle_writing(self):
        """Toggle the cheat on/off"""
        if not self.pm or not self.ptrs:
            messagebox.showwarning("Warning", "Not connected to game")
            return

        self.writing_enabled = not self.writing_enabled

        if self.writing_enabled:
            self.toggle_button.configure(text="Stop Cheats")
            self.status_var.set("Status: Cheats active")
        else:
            self.toggle_button.configure(text="Start Cheats")
            self.status_var.set("Status: Cheats inactive")

    def on_closing(self):
        """Handle window closing"""
        if self.writing_thread and self.writing_thread.is_alive():
            self.stop_writing_event.set()
            self.writing_thread.join(timeout=1.0)
        self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = SortTheCourtCheat(root)

    # Set icon if available
    icon_path = os.path.join(application_path, "icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)

    root.mainloop()