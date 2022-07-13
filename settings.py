import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

class Settings(tk.Tk):
    def __init__(self, client_window):
        tk.Tk.__init__(self)

        self.title("Settings")
        self.resizable(width = False, height = False)
        self.deiconify()

        self.client_window = client_window

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.master_frame = ttk.Frame(self)
        self.master_frame.grid(row=0, column=0)

        self.master_frame.grid_rowconfigure(0, weight=1)
        self.master_frame.grid_rowconfigure(0, weight=1)
        self.master_frame.grid_columnconfigure(0, weight=1)
        self.master_frame.grid_columnconfigure(1, weight=3)

        self.port_label = tk.Label(self.master_frame, text="Port")
        self.port_label.grid(row=0, column=0)

        self.port_input = tk.Entry(self.master_frame)
        self.port_input.grid(row=0, column=1)
        self.port_input.insert(0, client_window.PORT)

        self.apply_button = ttk.Button(self.master_frame, text="Apply", command=self.apply_button_callback)
        self.apply_button.grid(row=1, column=0, columnspan=2)

        self.mainloop()

    def apply_button_callback(self):
        # assert port is valid
        port = self.port_input.get()
        
        try:
            if self.client_window.is_hosting or self.client_window.is_joined:
                showerror("Error!", "Please leave server or stop hosting to change your port!")
                return
            self.client_window.PORT = int(port)
            self.client_window.update_title()
        except:
            showerror("Invalid Port", "Port chosen is not valid!")
            return
        self.client_window.settings_instance = None
        self.destroy()