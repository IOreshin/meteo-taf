import json, sys, os
from tkinter import messagebox

def get_resource_path(filename):
    """Возвращает путь к ресурсу (работает и из Python, и из exe)."""
    if hasattr(sys, '_MEIPASS'):  # если запущено из PyInstaller
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

def load_config(filename="config.json"):
    path = get_resource_path(filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Ошибка",
                             f"Не удалось загрузить rules.json: {e}")
        return {"checks" : []}
    