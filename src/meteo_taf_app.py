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
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.main_tab = Frame(self.notebook)
        self.notebook.add(self.main_tab, text="MAIN")

        self.plus_tab = Frame(self.notebook)
        self.notebook.add(self.plus_tab, text="+")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_switched)


        input_frame = tk.LabelFrame(self.main_tab, text="Ввод данных", padx=10, pady=10)
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

        weather_frame = tk.LabelFrame(self.main_tab, text="Явления", padx=10, pady=10)
        weather_frame.pack(fill="x", padx=10, pady=5)

        self.weather_container = Frame(weather_frame)
        self.weather_container.pack(fill="x")

        add_button = Button(weather_frame, text="Добавить явление", command=self.add_weather_row)
        add_button.pack(pady=5)
        tk.Button(root, text="Проверить и сформировать TAF", command=self.process_data).pack(pady=5)

        output_frame = tk.LabelFrame(self.main_tab, text="TAF", padx=10, pady=10)
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

    def on_tab_switched(self, event):
        selected = event.widget.select()
        tab_index = event.widget.index(selected)

        if event.widget.tab(tab_index, "text") == "+":
            self.add_group_tab()

    def add_group_tab(self):
        new_tab = Frame(self.notebook)
        index = len(self.notebook.tabs()) - 1
        tab_name = f"GROUP {index}"

        self.notebook.insert(index, new_tab, text=tab_name)
        self.notebook.select(new_tab)

        new_tab.entries = {}

        tk.Label(new_tab, text="Тип группы:").pack(anchor="w")
        type_combo = ttk.Combobox(new_tab, values=["TEMPO", "BECMG"], state="readonly")
        type_combo.pack(fill="x", padx=5, pady=2)
        new_tab.entries["group_type"] = type_combo

        tk.Label(new_tab, text="Время от (YYMMDDHH):").pack(anchor="w")
        time_from = tk.Entry(new_tab)
        time_from.pack(fill="x", padx=5, pady=2)
        new_tab.entries["time_from"] = time_from

        tk.Label(new_tab, text="Время до (YYMMDDHH):").pack(anchor="w")
        time_to = tk.Entry(new_tab)
        time_to.pack(fill="x", padx=5, pady=2)
        new_tab.entries["time_to"] = time_to

        tk.Label(new_tab, text="Направление ветра (°):").pack(anchor="w")
        wind_dir = tk.Entry(new_tab)
        wind_dir.pack(fill="x", padx=5, pady=2)
        new_tab.entries["wind_dir"] = wind_dir

        tk.Label(new_tab, text="Скорость ветра (MPS):").pack(anchor="w")
        wind_speed = tk.Entry(new_tab)
        wind_speed.pack(fill="x", padx=5, pady=2)
        new_tab.entries["wind_speed"] = wind_speed

        tk.Label(new_tab, text="Видимость (м):").pack(anchor="w")
        visibility = tk.Entry(new_tab)
        visibility.pack(fill="x", padx=5, pady=2)
        new_tab.entries["visibility"] = visibility

        tk.Label(new_tab, text="Облачность:").pack(anchor="w")
        clouds = tk.Entry(new_tab)
        clouds.pack(fill="x", padx=5, pady=2)
        new_tab.entries["clouds"] = clouds

        weather_frame = tk.LabelFrame(new_tab, text="Явления", padx=5, pady=5)
        weather_frame.pack(fill="x", padx=5, pady=5)
        new_tab.weather_rows = []

        add_weather_btn = Button(weather_frame, text="Добавить явление",
                                command=lambda nf=new_tab: self.add_weather_row(nf))
        add_weather_btn.pack(pady=2)

        Button(new_tab, text="Удалить группу",
            command=lambda tab=new_tab: self.remove_tab(tab)).pack(pady=5)

    def remove_tab(self, tab_frame):
        tabs = list(self.notebook.tabs())
        for i, tab_id in enumerate(tabs):
            if self.notebook.nametowidget(tab_id) == tab_frame:
                tabs.remove(tab_id)
                if i == len(tabs) - 1:
                    self.notebook.select(tabs[i-1])
                else:
                    self.notebook.select(tabs[i])
                self.notebook.forget(tab_id)
                break
        
        self.rename_group_tabs()

    def rename_group_tabs(self):
        tabs = list(self.notebook.tabs())
        if len(tabs) <= 2:
            return
        group_index = 1
        for tab_id in tabs[1:-1]:
            self.notebook.tab(tab_id, text=f"GROUP {group_index}")
            group_index += 1
        
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