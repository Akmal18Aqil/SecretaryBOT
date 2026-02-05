import tkinter as tk
from tkinter import messagebox
import os

ENV_FILE = ".env"

class ConfigWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("The Secretary - Setup Awal")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        # Style constants
        PADDING = 10
        LABEL_WIDTH = 20

        # Title
        title_label = tk.Label(root, text="Selamat Datang di The Secretary!", font=("Arial", 14, "bold"))
        title_label.pack(pady=20)

        inst_label = tk.Label(root, text="Silakan masukkan kunci rahasia (API Key) Anda di bawah ini.\nData ini hanya tersimpan di komputer Anda.", wraplength=450, justify="center")
        inst_label.pack(pady=(0, 20))

        # Form Frame
        form_frame = tk.Frame(root)
        form_frame.pack(padx=20, pady=10, fill="x")

        # Google Gemini
        self.add_field(form_frame, "Google Gemini API Key:", "GOOGLE_API_KEY", 0)
        
        # Telegram Bot
        self.add_field(form_frame, "Telegram Bot Token:", "TELEGRAM_BOT_TOKEN", 1)

        # Supabase URL
        self.add_field(form_frame, "Supabase URL:", "SUPABASE_URL", 2)

        # Supabase Key
        self.add_field(form_frame, "Supabase Key:", "SUPABASE_KEY", 3)

        # Save Button
        self.save_btn = tk.Button(root, text="Simpan & Mulai", command=self.save_config, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), height=2)
        self.save_btn.pack(pady=30, fill="x", padx=40)

        self.entries = {}

    def add_field(self, parent, label_text, key, row):
        lbl = tk.Label(parent, text=label_text, anchor="w", width=25, font=("Arial", 9, "bold"))
        lbl.grid(row=row*2, column=0, sticky="w", pady=(10, 0))
        
        entry = tk.Entry(parent, width=50)
        entry.grid(row=row*2+1, column=0, sticky="w", pady=(2, 0))
        
        # Store reference
        self.entries[key] = entry

    def save_config(self):
        config_data = {}
        missing_fields = []

        for key, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                missing_fields.append(key)
            config_data[key] = value

        if missing_fields:
            messagebox.showerror("Error", f"Mohon isi semua kolom!\nKolom kosong: {', '.join(missing_fields)}")
            return

        try:
            with open(ENV_FILE, "w") as f:
                for key, value in config_data.items():
                    f.write(f"{key}={value}\n")
            
            messagebox.showinfo("Sukses", "Konfigurasi berhasil disimpan! Bot akan segera berjalan.")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan file: {str(e)}")

def run_wizard():
    if os.path.exists(ENV_FILE):
        # Optional: Ask if user wants to reconfigure if env already exists
        # For now, simplest path: if env exists, assume it's good (launcher logic will handle skip)
        pass

    root = tk.Tk()
    app = ConfigWizard(root)
    root.mainloop()

if __name__ == "__main__":
    run_wizard()
