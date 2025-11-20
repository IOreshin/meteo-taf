import tkinter as tk
from tkinter import messagebox, ttk, Frame, Button
from weather_validator import validate_all_data
from taf_formatter import generate_taf
from loader import load_config

class MeteoTafApp:
    def __init__(self, root):
        self.root = root
        self.root.title("meteo-taf")
        self.root.geometry("550x900")
        self.root.resizable(False, True)
        self.config = load_config()

        self.weather_frames = []
        self.weather_rows = []

        self.tabs_entries = {}

        self.group_counter = 1
        self.tab_id_map = {}

        self.init_ui()

    def init_ui(self):
        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.main_tab = Frame(self.notebook)
        self.notebook.add(self.main_tab, text="MAIN")

        self.plus_tab = Frame(self.notebook)
        self.notebook.add(self.plus_tab, text="+")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_switched)

        # MAIN tab UI
        self.init_tab_ui(self.main_tab, "main", 0)
        self.init_weather_frame(self.main_tab, 0)

        # Button
        self.generate_btn = tk.Button(
            self.root,
            text="Проверить и сформировать TAF",
            command=self.process_data
        )
        self.generate_btn.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        # Output Area
        output_frame = tk.LabelFrame(self.root, text="TAF", padx=10, pady=10)
        output_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.text_area = tk.Text(output_frame, wrap="word", height=15)
        self.text_area.grid(row=0, column=0, sticky="nsew")
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

    def init_tab_ui(self, tab, tab_type=None, group_id=0):
        input_frame = tk.LabelFrame(tab, text="Ввод данных", padx=10, pady=10)
        input_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

        fields = [
            ("ICAO", "icao", "entry", "main"),
            ("Тип группы", "group_type", "combo", "group", ["TEMPO", "BECMG"]),
            ("Время выпуска (DDHHMM)", "issue_time", "entry", "main"),
            ("Время действия от (DDHH)", "time_from", "entry", None),
            ("Время действия до (DDHH)", "time_to", "entry", None),
            ("Направление ветра (°)", "wind_dir", "entry", None),
            ("Скорость ветра (MPS)", "wind_speed", "entry", None),
            ("Порыв ветра", "wind_gust", "entry", None),
            ("Видимость (м)", "visibility", "entry", None),
        ]

        self.tabs_entries[group_id] = {}
        row_index = 0

        for label, key, field_type, _tab_type, *args in fields:
            if _tab_type is None or tab_type == _tab_type:
                tk.Label(input_frame, text=label, width=22, anchor="e").grid(
                    row=row_index, column=0, pady=3, sticky="e"
                )
                if field_type == "combo":
                    widget = ttk.Combobox(
                        input_frame,
                        values=args[0],
                        width=25,
                        state="readonly"
                    )
                else:
                    widget = ttk.Entry(input_frame, width=25)

                widget.grid(row=row_index, column=1, pady=3, sticky="w")
                self.tabs_entries[group_id][key] = widget
                row_index += 1

        if group_id != 0:
            self.tabs_entries[group_id]["issue_time"] = self.tabs_entries[0]["issue_time"]

        # Облачность
        clouds_frame = tk.LabelFrame(input_frame, text="Облачность", padx=5, pady=5)
        clouds_frame.grid(row=row_index, column=0, columnspan=2, sticky="nw", padx=5, pady=5)

        self.tabs_entries[group_id]["clouds_entries"] = []

        add_btn = Button(
            clouds_frame,
            text="Добавить",
            command=lambda f=clouds_frame: self.add_cloud_row(f, group_id)
        )
        add_btn.grid(row=0, column=0, pady=5)

        self.add_cloud_row(clouds_frame, group_id)

    def add_cloud_row(self, frame, group_id):
        idx = len(self.tabs_entries[group_id]["clouds_entries"])

        row_frame = tk.LabelFrame(frame, text=f"Слой {idx + 1}", pady=5, padx=5)
        row_frame.grid(row=idx + 1, column=0, sticky="nw")

        tk.Label(row_frame, text="Облачность").grid(row=0, column=0)
        amount_cb = ttk.Combobox(row_frame, values=[x["amount"] for x in self.config["clouds_amount"]], width=10)
        amount_cb.grid(row=1, column=0, padx=2)

        tk.Label(row_frame, text="Высота").grid(row=0, column=1)
        height_cb = ttk.Combobox(row_frame, values=[f"{i:03d}" for i in range(1, 50)], width=6)
        height_cb.grid(row=1, column=1, padx=2)

        tk.Label(row_frame, text="Тип").grid(row=0, column=2)
        type_cb = ttk.Combobox(row_frame, values=[x["type"] for x in self.config["clouds_type"]], width=12)
        type_cb.grid(row=1, column=2, padx=2)

        if idx > 0:
            Button(
                row_frame,
                text="✖",
                command=lambda fr=row_frame: self.delete_cloud_row(fr, group_id)
            ).grid(row=0, column=3, padx=4)

        self.tabs_entries[group_id]["clouds_entries"].append(
            (row_frame, amount_cb, height_cb, type_cb)
        )

    def delete_cloud_row(self, frame, group_id):
        frame.destroy()
        self.tabs_entries[group_id]["clouds_entries"] = [
            entry for entry in self.tabs_entries[group_id]["clouds_entries"]
            if entry[0] != frame
        ]

    def init_weather_frame(self, tab, group_id):
        weather_frame = tk.LabelFrame(tab, text="Явления", padx=10, pady=10)
        weather_frame.grid(row=1, column=0, sticky="nw")

        container = Frame(weather_frame)
        container.grid(row=0, column=0, sticky="nw")

        Button(
            weather_frame,
            text="Добавить явление",
            command=lambda fr=container: self.add_weather_row(fr, group_id)
        ).grid(row=1, column=0, pady=5)

        self.tabs_entries[group_id]["weather_events"] = []

    def add_weather_row(self, frame, group_id):
        intensities = [x["intensity"] for x in self.config.get("intensity", [])]
        descriptors = [x["descriptor"] for x in self.config.get("descriptor", [])]
        events = [x["event"] for x in self.config.get("weather_events", [])]

        idx = len(self.tabs_entries[group_id]["weather_events"])
        row_frame = Frame(frame)
        row_frame.grid(row=idx, column=0, sticky="nw", pady=3)

        tk.Label(row_frame, text="Инт.").grid(row=0, column=0)
        cb_int = ttk.Combobox(row_frame, values=intensities, width=4, state="readonly")
        cb_int.grid(row=1, column=0)

        tk.Label(row_frame, text="Хар.").grid(row=0, column=1)
        cb_desc = ttk.Combobox(row_frame, values=descriptors, width=5, state="readonly")
        cb_desc.grid(row=1, column=1)

        tk.Label(row_frame, text="Явл.").grid(row=0, column=2)
        cb_event = ttk.Combobox(row_frame, values=events, width=6, state="readonly")
        cb_event.grid(row=1, column=2)

        Button(
            row_frame,
            text="✖",
            command=lambda fr=row_frame: self.remove_weather_row(fr)
        ).grid(row=0, column=3, padx=5)

        self.tabs_entries[group_id]["weather_events"].append(
            (row_frame, cb_int, cb_desc, cb_event)
        )

    def remove_weather_row(self, frame):
        frame.destroy()

    def on_tab_switched(self, event):
        selected = event.widget.select()
        idx = event.widget.index(selected)

        if event.widget.tab(idx, "text") == "+":
            self.add_group_tab()

    def add_group_tab(self):
        new_tab = Frame(self.notebook)

        group_id = self.group_counter
        self.group_counter += 1

        tab_index = len(self.notebook.tabs()) - 1
        tab_name = f"GROUP {tab_index}"

        self.notebook.insert(tab_index, new_tab, text=tab_name)
        self.notebook.select(new_tab)

        self.tab_id_map[new_tab] = group_id
        self.tabs_entries[group_id] = {}

        self.init_tab_ui(new_tab, "group", group_id)
        self.init_weather_frame(new_tab, group_id)

        Button(
            new_tab,
            text="Удалить группу",
            command=lambda t=new_tab: self.remove_tab(t)
        ).grid(row=2, column=0, pady=10)

    def remove_tab(self, tab_frame):
        tabs = list(self.notebook.tabs())

        group_id = self.tab_id_map.pop(tab_frame, None)
        if group_id is not None:
            self.tabs_entries.pop(group_id, None)

        for i, tab_id in enumerate(tabs):
            if self.notebook.nametowidget(tab_id) == tab_frame:
                self.notebook.forget(tab_id)
                break
        
        self.rename_group_tabs()

    def rename_group_tabs(self):
        tabs = list(self.notebook.tabs())
        if len(tabs) <= 2:
            return

        idx = 1
        for tab_id in tabs[1:-1]:
            self.notebook.tab(tab_id, text=f"GROUP {idx}")
            idx += 1

    def collect_weather_events(self, group_id):
        events = []
        for row in self.tabs_entries[group_id]["weather_events"]:
            _, cb_int, cb_desc, cb_event = row
            i = cb_int.get().strip()
            d = cb_desc.get().strip()
            e = cb_event.get().strip()
            if e:
                events.append(f"{i}{d}{e}")
        return events

    def collect_clouds_entries(self, group_id):
        clouds = []
        for row in self.tabs_entries[group_id]["clouds_entries"]:
            _, amount, height, ctype = row
            a = amount.get().strip()
            h = height.get().strip()
            c = ctype.get().strip()
            if a:
                clouds.append({"amount": a, "height": h, "cloud_type": c})
        return clouds

    def process_data(self):
        all_data = {}

        for group_id, widgets in self.tabs_entries.items():
            data = {}

            for key, widget in widgets.items():
                if key == "weather_events":
                    data[key] = self.collect_weather_events(group_id)
                elif key == "clouds_entries":
                    data[key] = self.collect_clouds_entries(group_id)
                else:
                    value = widget.get().strip() if hasattr(widget, "get") else ""
                    if key in ("wind_dir", "wind_speed", "visibility"):
                        value = int(value or 0)
                    data[key] = value

            errors = validate_all_data(data, self.config)
            if errors:
                messagebox.showerror(f"Ошибки в группе {group_id}", "\n".join(errors))
                return

            all_data[group_id] = data

        taf_output = " ".join(generate_taf(d) for d in all_data.values()) + "="

        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, taf_output)


if __name__ == "__main__":
    root = tk.Tk()
    app = MeteoTafApp(root)
    root.mainloop()
