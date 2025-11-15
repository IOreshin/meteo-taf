import tkinter as tk
from tkinter import messagebox, ttk, Frame, Button
from weather_validator import validate_all_data
from taf_formatter import generate_taf
from loader import load_rules


class MeteoTafApp:
    def __init__(self, root):
        self.root = root
        self.root.title("meteo-taf")

        self.rules = load_rules()

        self.init_ui()

    def init_ui(self):
        input_frame = tk.LabelFrame(root, text="Ввод данных", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        self.entries = {}
        self.weather_rows = []

        fields = [
            ("ICAO", "icao", "entry"),
            ("Время выпуска", "issue_time", "entry"),
            ("Время от (YYMMDDHH)", "time_from", "entry"),
            ("Время до (YYMMDDHH)", "time_to", "entry"),
            ("Направление ветра (°)", "wind_dir", "entry"),
            ("Скорость ветра (MPS)", "wind_speed", "entry"),
            ("Видимость (м)", "visibility", "entry"),
            ("Облачность", "clouds", "entry"),
        ]

        for i, (label, key, field_type) in enumerate(fields):
            tk.Label(input_frame, text=label, width=25, anchor="e").grid(row=i, column=0, pady=2)
            entry = tk.Entry(input_frame, width=25)
            entry.grid(row=i, column=1, pady=2)
            self.entries[key] = entry

        weather_frame = tk.LabelFrame(self.root, text="Явления", padx=10, pady=10)
        weather_frame.pack(fill="x", padx=10, pady=5)

        self.weather_container = Frame(weather_frame)
        self.weather_container.pack(fill="x")

        add_button = Button(weather_frame, text="Добавить явление", command=self.add_weather_row)
        add_button.pack(pady=5)
        tk.Button(root, text="Проверить и сформировать TAF", command=self.process_data).pack(pady=5)

        output_frame = tk.LabelFrame(root, text="TAF", padx=10, pady=10)
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.text_area = tk.Text(output_frame, wrap="word", height=10)
        self.text_area.pack(fill="both", expand=True)

    def add_weather_row(self):
        intensities = [x["intensity"] for x in self.rules.get("intensity", [])]
        descriptors = [x["descriptor"] for x in self.rules.get("descriptor", [])]
        events = [x["event"] for x in self.rules.get("weather_events", [])]

        row_frame = Frame(self.weather_container)
        row_frame.pack(fill="x", pady=2)

        cb_int = ttk.Combobox(row_frame, values=intensities, width=5, state="readonly")
        int_label = tk.Label(row_frame, text="Интенсивность", anchor="e")
        cb_desc = ttk.Combobox(row_frame, values=descriptors, width=5, state="readonly")
        desc_label = tk.Label(row_frame, text="Характер", anchor="e")
        cb_event = ttk.Combobox(row_frame, values=events, width=8, state="readonly")
        event_label = tk.Label(row_frame, text="Код явления", anchor="e")

        cb_int.grid(row=1, column=0, padx=2)
        int_label.grid(row=0,column=0, padx=2)
        cb_desc.grid(row=1, column=1, padx=2)
        desc_label.grid(row=0, column=1, padx=2)
        cb_event.grid(row=1, column=2, padx=2)
        event_label.grid(row=0, column=2, padx=2)

        remove_btn = Button(row_frame, text="✖", width=2,
                            command=lambda fr=row_frame: self.remove_weather_row(fr))
        remove_btn.grid(row=0, column=3, padx=2)

        self.weather_rows.append((row_frame, cb_int, cb_desc, cb_event))

    def remove_weather_row(self, frame):
        frame.destroy()
        self.weather_rows = [row for row in self.weather_rows if row[0] != frame]

    def collect_weather_events(self):
        results = []
        for frame, cb_int, cb_desc, cb_event in self.weather_rows:
            i = cb_int.get().strip()
            d = cb_desc.get().strip()
            e = cb_event.get().strip()
            if e:
                results.append(f"{i}{d}{e}")
        
        return results

    def process_data(self):
        try:
            data = {
                "icao": self.entries["icao"].get().strip().upper(),
                "issue_time" : self.entries["issue_time"].get().strip().upper(),
                "time_from": self.entries["time_from"].get().strip(),
                "time_to": self.entries["time_to"].get().strip(),
                "wind_dir": int(self.entries["wind_dir"].get() or 0),
                "wind_speed": int(self.entries["wind_speed"].get() or 0),
                "visibility": int(self.entries["visibility"].get() or 0),
                "clouds": self.entries["clouds"].get().strip().upper(),
                "weather_events" : self.collect_weather_events(),
            }
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат числовых значений.")
            return

        errors = validate_all_data(data, self.rules)
        if errors:
            self.text_area.delete("1.0", tk.END)
            messagebox.showwarning("Ошибки в данных", "\n".join(errors))
            return

        taf = generate_taf(data)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, taf)

if __name__ == "__main__":
    root = tk.Tk()
    app = MeteoTafApp(root)
    root.mainloop()