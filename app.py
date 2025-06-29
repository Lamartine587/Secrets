import tkinter as tk
from tkinter import messagebox, ttk
from cryptography.fernet import Fernet, InvalidToken
import os
import random
import time

# --- Configuration Constants ---
KEY_FILE_PATH = "mykey.key"
APP_TITLE = "NEONCRYPT v1.0"
ENCODING = 'utf-8'

# --- THEME COLORS & FONTS ---
BG_DARK = "#0A0A0A"
BG_MEDIUM = "#2A2A2A"
FG_LIGHT = "#E0E0E0"
ACCENT_BLUE = "#00FFFF"
ACCENT_GREEN = "#00FF00"
ACCENT_MAGENTA = "#FF00FF"
ACCENT_PURPLE = "#8000FF"
ACCENT_RED = "#FF4040"
BORDER_COLOR = "#00FF00"
BINARY_COLORS = [ACCENT_GREEN, ACCENT_BLUE, ACCENT_MAGENTA, ACCENT_PURPLE, ACCENT_RED]

FONT_GENERAL = ("Consolas", 10, "bold")
FONT_TITLE = ("Consolas", 14, "bold")
FONT_TEXT_AREA = ("Consolas", 10, "bold")
FONT_BINARY = ("Consolas", 10)
GLITCH_CHARS = ['0', '1', '%', '$', '#', '@', '&']

# --- Key Management Function ---
def load_or_generate_key():
    """Loads the encryption key from file, or generates a new one if not found or invalid."""
    key = None
    if os.path.exists(KEY_FILE_PATH):
        try:
            with open(KEY_FILE_PATH, "rb") as key_file:
                loaded_key = key_file.read()
            try:
                Fernet(loaded_key)
                key = loaded_key
            except ValueError:
                messagebox.showwarning("Key Invalid",
                                       "The existing key file was invalid. A new key has been generated.")
        except IOError as e:
            messagebox.showerror("File Error",
                                 f"Could not read key file '{KEY_FILE_PATH}': {e}.\nAttempting to generate a new key.")

    if key is None:
        try:
            key = Fernet.generate_key()
            with open(KEY_FILE_PATH, "wb") as key_file:
                key_file.write(key)
            messagebox.showinfo("Key Generated",
                                "A new encryption key has been generated and saved as 'mykey.key'.\nKeep this file secure and hidden!")
        except IOError as e:
            messagebox.showerror("Critical Error",
                                 f"Failed to save generated key to '{KEY_FILE_PATH}': {e}\nApplication cannot proceed. Check file permissions.")
            return None
    return key

# --- Main Application Logic ---
class SecureMessageApp:
    def __init__(self, master):
        self.master = master
        master.title(APP_TITLE)
        master.config(bg=BG_DARK)

        # Configure ttk style for themed widgets
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=BG_DARK)
        style.configure('TLabel', background=BG_DARK, foreground=ACCENT_BLUE, font=FONT_TITLE)
        style.configure('TButton',
                        background=BG_MEDIUM,
                        foreground=ACCENT_GREEN,
                        font=FONT_GENERAL,
                        relief="flat",
                        borderwidth=2,
                        highlightbackground=ACCENT_GREEN,
                        highlightcolor=ACCENT_GREEN,
                        highlightthickness=1,
                        padding=[10, 5])
        style.map('TButton',
                  background=[('active', ACCENT_BLUE)],
                  foreground=[('active', BG_DARK)])

        self.key = load_or_generate_key()
        if self.key is None:
            master.destroy()
            return
        self.cipher = Fernet(self.key)

        # Create canvas for binary animation
        self.canvas = tk.Canvas(master, bg=BG_DARK, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        # Main frame for UI elements
        self.main_frame = ttk.Frame(master, style='TFrame')
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.rowconfigure(4, weight=1)

        # Input Section
        ttk.Label(self.main_frame, text="> INPUT DATA STREAM:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry = tk.Text(
            self.main_frame,
            height=8, width=70,
            bg=BG_MEDIUM, fg=FG_LIGHT,
            insertbackground=ACCENT_BLUE,
            selectbackground=ACCENT_BLUE,
            selectforeground=BG_DARK,
            font=FONT_TEXT_AREA,
            relief="flat", borderwidth=1, highlightbackground=BORDER_COLOR, highlightthickness=1
        )
        self.entry.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Buttons Frame
        btn_frame = ttk.Frame(self.main_frame, style='TFrame')
        btn_frame.grid(row=2, column=0, pady=10)
        ttk.Button(btn_frame, text="> ENCRYPT", command=self.encrypt_message).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="> DECRYPT", command=self.decrypt_message).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="> CLEAR INPUT", command=self.clear_input).pack(side=tk.LEFT, padx=10)

        # Output Section
        ttk.Label(self.main_frame, text="> OUTPUT DATA STREAM:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.output = tk.Text(
            self.main_frame,
            height=8, width=70,
            bg=BG_MEDIUM, fg=ACCENT_GREEN,
            font=FONT_TEXT_AREA,
            relief="flat", borderwidth=1, highlightbackground=BORDER_COLOR, highlightthickness=1,
            state=tk.DISABLED
        )
        self.output.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

        # Output Buttons Frame
        output_btn_frame = ttk.Frame(self.main_frame, style='TFrame')
        output_btn_frame.grid(row=5, column=0, pady=5)
        ttk.Button(output_btn_frame, text="> COPY OUTPUT", command=self.copy_output).pack(side=tk.LEFT, padx=10)
        ttk.Button(output_btn_frame, text="> CLEAR OUTPUT", command=self.clear_output).pack(side=tk.LEFT, padx=10)

        # Status Bar
        self.status_label = ttk.Label(self.main_frame, text="> STATUS: INITIALIZED", font=("Consolas", 8, "bold"), foreground=ACCENT_GREEN)
        self.status_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")

        # Binary animation setup
        self.current_status = "> STATUS: INITIALIZED"
        self.binary_chars = []
        self.window_width = 800
        self.window_height = 600
        self.columns = 80
        self.char_size = 12
        self.drop_speed = 3
        self.setup_binary_animation()
        self.master.bind("<Configure>", self.on_resize)
        self.animate_binary()
        self.animate_status()

    def setup_binary_animation(self):
        """Initialize binary falling characters with glitch effect."""
        self.canvas.delete("all")
        self.binary_chars = []
        col_width = self.window_width // self.columns
        for i in range(self.columns):
            x = i * col_width + col_width // 2
            y = random.randint(-self.window_height, 0)
            speed = random.uniform(1.5, self.drop_speed * 2)
            length = random.randint(8, 20)
            chars = [(x, y + j * self.char_size, random.choice(GLITCH_CHARS), random.choice(BINARY_COLORS)) for j in range(length)]
            self.binary_chars.append({'chars': chars, 'speed': speed})

    def animate_binary(self):
        """Update and redraw binary falling animation with glitch effect."""
        self.canvas.delete("all")
        for col in self.binary_chars:
            for i, (x, y, char, color) in enumerate(col['chars']):
                alpha = max(0.05, 0.4 - (i / len(col['chars']) * 0.3))
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                color = f"#{int(r * alpha):02x}{int(g * alpha):02x}{int(b * alpha):02x}"
                if random.random() < 0.05:
                    char = random.choice(GLITCH_CHARS)
                self.canvas.create_text(x, y, text=char, font=FONT_BINARY, fill=color)
            col['chars'] = [(x, y + col['speed'], char, color) for x, y, char, color in col['chars']]
            if col['chars'][-1][1] > self.window_height + self.char_size:
                col['chars'] = [(col['chars'][0][0], y - self.window_height - len(col['chars']) * self.char_size, random.choice(GLITCH_CHARS), random.choice(BINARY_COLORS))
                                for _, y, _, color in col['chars']]
        self.master.after(50, self.animate_binary)

    def animate_status(self):
        """Animate status bar with typing effect."""
        status_text = self.current_status
        if len(status_text) > 10:
            for i in range(len(status_text) + 1):
                self.status_label.config(text=status_text[:i])
                self.master.update()
                time.sleep(0.05)
            self.status_label.config(text=status_text)
        self.master.after(2000, self.animate_status)

    def on_resize(self, event):
        """Handle window resize to adjust animation."""
        self.window_width = event.width
        self.window_height = event.height
        self.setup_binary_animation()

    def update_status(self, message, color=ACCENT_GREEN):
        self.current_status = f"> STATUS: {message}"
        self.status_label.config(text=self.current_status, foreground=color)

    def update_output(self, text):
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)
        self.output.config(state=tk.DISABLED)
        self.update_status("OUTPUT UPDATED", ACCENT_GREEN)

    def clear_input(self):
        self.entry.delete("1.0", tk.END)
        self.update_status("INPUT CLEARED", FG_LIGHT)

    def clear_output(self):
        self.update_output("")
        self.update_status("OUTPUT CLEARED", FG_LIGHT)

    def copy_output(self):
        text_to_copy = self.output.get("1.0", tk.END).strip()
        if text_to_copy:
            self.master.clipboard_clear()
            self.master.clipboard_append(text_to_copy)
            messagebox.showinfo("Copied", "Output copied to clipboard!")
            self.update_status("OUTPUT COPIED", ACCENT_BLUE)
        else:
            messagebox.showwarning("Empty", "Nothing to copy from output.")
            self.update_status("COPY FAILED: NO OUTPUT", ACCENT_BLUE)

    def encrypt_message(self):
        text = self.entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter a message to encrypt.")
            self.update_status("ENCRYPTION FAILED: NO INPUT", ACCENT_BLUE)
            return
        try:
            encrypted = self.cipher.encrypt(text.encode(ENCODING))
            self.update_output(encrypted.decode(ENCODING))
            self.update_status("ENCRYPTION SUCCESSFUL", ACCENT_GREEN)
        except Exception as e:
            messagebox.showerror("Encryption Error", f"Encryption failed: {e}")
            self.update_status(f"ENCRYPTION ERROR: {e}", ACCENT_BLUE)

    def decrypt_message(self):
        text = self.entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter an encrypted message to decrypt.")
            self.update_status("DECRYPTION FAILED: NO INPUT", ACCENT_BLUE)
            return
        try:
            decrypted = self.cipher.decrypt(text.encode(ENCODING))
            self.update_output(decrypted.decode(ENCODING))
            self.update_status("DECRYPTION SUCCESSFUL", ACCENT_GREEN)
        except InvalidToken:
            messagebox.showerror("Decryption Failed", "Invalid or corrupted token, or wrong key. Cannot decrypt.")
            self.update_status("DECRYPTION FAILED: INVALID TOKEN", ACCENT_BLUE)
        except Exception as e:
            messagebox.showerror("Decryption Error",
                                 f"Decryption failed: {e}\nEnsure the input is a valid Fernet-encrypted message.")
            self.update_status(f"DECRYPTION ERROR: {e}", ACCENT_BLUE)

def main():
    root = tk.Tk()
    app = SecureMessageApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    
