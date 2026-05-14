import os
import sys
import json
import random
import shutil
import zipfile
import customtkinter as ctk
from tkinter import filedialog

# =========================================================
# PATH FIX (EXE SAFE)
# =========================================================

def resource_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), filename)
    return os.path.join(os.path.dirname(__file__), filename)

# =========================================================
# SAFE LOAD
# =========================================================

def load_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return fallback

LANG = load_json(resource_path("language_de.json"), {
    "title": "File Tool",
    "source": "Quelle",
    "target": "Ziel",
    "browse": "Durchsuchen"
})

SETTINGS = load_json(resource_path("settings.json"), {
    "theme": "dark",
    "source": "",
    "target": "",
    "mode": "copy_only",
    "language": "de",
    "amount": "10"
})

# =========================================================
# UI SETUP
# =========================================================

ctk.set_appearance_mode(SETTINGS.get("theme", "dark"))
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("780x700")
app.minsize(780, 700)
app.maxsize(780, 700)
app.title(LANG.get("title", "File Tool"))

SUPPORTED = (
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff",
    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".flv", ".mpeg"
)

# =========================================================
# VARIABLES
# =========================================================

mode_var = ctk.StringVar(value=SETTINGS.get("mode", "copy_only"))
lang_var = ctk.StringVar(value=SETTINGS.get("language", "de"))

# =========================================================
# SAVE SETTINGS
# =========================================================

def save_settings():
    SETTINGS["source"] = source_entry.get()
    SETTINGS["target"] = target_entry.get()
    SETTINGS["mode"] = mode_var.get()
    SETTINGS["language"] = lang_var.get()
    SETTINGS["amount"] = amount_entry.get()

    with open(resource_path("settings.json"), "w", encoding="utf-8") as f:
        json.dump(SETTINGS, f, indent=4, ensure_ascii=False)

# =========================================================
# FOLDER
# =========================================================

def choose_source():
    folder = filedialog.askdirectory()
    if folder:
        source_entry.delete(0, "end")
        source_entry.insert(0, folder)
        save_settings()

def choose_target():
    folder = filedialog.askdirectory()
    if folder:
        target_entry.delete(0, "end")
        target_entry.insert(0, folder)
        save_settings()

# =========================================================
# FILES
# =========================================================

def get_files(folder):
    result = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(SUPPORTED):
                result.append(os.path.join(root, f))
    return result

# =========================================================
# SETTINGS WINDOW (FIXED)
# =========================================================

def open_settings():

    win = ctk.CTkToplevel(app)
    win.geometry("420x450")
    win.title("Einstellungen")

    win.transient(app)
    win.grab_set()
    win.focus_force()

    # ================= MODE =================

    ctk.CTkLabel(win, text="Modus").pack(pady=10)

    frame = ctk.CTkFrame(win)
    frame.pack(fill="x", padx=20)

    ctk.CTkRadioButton(frame, text="Nur kopieren", variable=mode_var, value="copy_only").pack(anchor="w", padx=10, pady=5)
    ctk.CTkRadioButton(frame, text="Nur ZIP", variable=mode_var, value="zip_only").pack(anchor="w", padx=10, pady=5)
    ctk.CTkRadioButton(frame, text="Kopieren + ZIP", variable=mode_var, value="copy_and_zip").pack(anchor="w", padx=10, pady=5)

    # ================= LANGUAGE =================

    ctk.CTkLabel(win, text="Sprache").pack(pady=10)

    ctk.CTkComboBox(
        win,
        values=["de", "en"],
        variable=lang_var
    ).pack()

    # ================= AMOUNT =================

    ctk.CTkLabel(win, text="Anzahl Dateien").pack(pady=10)

    amount_entry_settings = ctk.CTkEntry(win)
    amount_entry_settings.pack()
    amount_entry_settings.insert(0, amount_entry.get())

    def apply():
        amount_entry.delete(0, "end")
        amount_entry.insert(0, amount_entry_settings.get())
        save_settings()

    ctk.CTkButton(win, text="Übernehmen", command=apply).pack(pady=20)

# =========================================================
# START
# =========================================================

def start_process():

    save_settings()

    source = source_entry.get()
    target = target_entry.get()
    mode = mode_var.get()

    try:
        amount = int(amount_entry.get())
    except:
        amount = 1

    if not os.path.exists(source):
        return

    os.makedirs(target, exist_ok=True)

    files = get_files(source)

    if not files:
        return

    selected = random.sample(files, min(amount, len(files)))

    zip_path = os.path.join(target, "RandomFiles.zip")

    if mode == "copy_only":
        for f in selected:
            shutil.copy(f, target)

    elif mode == "zip_only":
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for f in selected:
                z.write(f, os.path.basename(f))

    elif mode == "copy_and_zip":
        for f in selected:
            shutil.copy(f, target)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for f in selected:
                z.write(f, os.path.basename(f))

# =========================================================
# UI
# =========================================================

frame = ctk.CTkFrame(app)
frame.pack(padx=20, pady=20, fill="both", expand=True)

ctk.CTkLabel(frame, text=LANG["title"], font=("Arial", 26, "bold")).pack(pady=20)

source_entry = ctk.CTkEntry(frame, width=600)
source_entry.pack()
source_entry.insert(0, SETTINGS["source"])

ctk.CTkButton(frame, text=LANG["browse"], command=choose_source).pack(pady=5)

target_entry = ctk.CTkEntry(frame, width=600)
target_entry.pack()
target_entry.insert(0, SETTINGS["target"])

ctk.CTkButton(frame, text=LANG["browse"], command=choose_target).pack(pady=5)

amount_entry = ctk.CTkEntry(frame, width=200)
amount_entry.pack()
amount_entry.insert(0, SETTINGS["amount"])

ctk.CTkButton(frame, text="START", command=start_process, height=50).pack(pady=20)

# =========================================================
# SETTINGS BUTTON
# =========================================================

ctk.CTkButton(app, text="⚙", width=40, height=40, command=open_settings).place(x=30, y=630)

# =========================================================
# WATERMARK
# =========================================================

ctk.CTkLabel(app, text="© SallixO", font=("Arial", 12), text_color="#666").place(relx=0.92, rely=0.93)

# =========================================================
# RUN
# =========================================================

app.mainloop()