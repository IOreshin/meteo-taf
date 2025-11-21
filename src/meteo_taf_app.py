import tkinter as tk
from tkinter import messagebox, ttk, Frame, Button, Menu
from weather_validator import validate_all_data
from taf_formatter import generate_taf
from loader import load_config
from json_editor import JsonEditor

class MeteoTafApp:
    def __init__(self, root):
        self.root = root
        self.root.title("meteo-taf")
        self.root.geometry("450x800")
        self.root.resizable(False, True)

        self.config = load_config()

        self.weather_frames = []
        self.weather_rows = []

        self.tabs_entries = {}

        self.group_counter = 1
        self.tab_id_map = {}

        self.init_ui()

    def init_ui(self):
        main_menu = Menu()
        file_menu = Menu(tearoff=0)
        file_menu.add_command(label="Редактирование условий", command=self.init_json_editor)
        file_menu.add_command(label="Выход", command=self.close_app)

        main_menu.add_cascade(label="Файл", menu=file_menu)
        self.root.config(menu = main_menu)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.main_tab = Frame(self.notebook)
        self.notebook.add(self.main_tab, text="MAIN")

        self.plus_tab = Frame(self.notebook)
        self.notebook.add(self.plus_tab, text="+")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_switched)

        self.init_tab_ui(self.main_tab, "main", 0)
        self.init_weather_frame(self.main_tab, 0)

        tk.Button(root, text="Проверить и сформировать TAF", command=self.process_data).pack(pady=5)

        output_frame = tk.LabelFrame(self.root, text="TAF", padx=10, pady=10)
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.text_area = tk.Text(output_frame, wrap="word", height=10)
        self.text_area.pack(fill="both", expand=True)

    def init_tab_ui(self, tab, tab_type : str = None, group_id : int = 0):
        input_frame = tk.LabelFrame(tab, text="Ввод данных", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

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
        for i, (label, key, field_type, _tab_type, *args) in enumerate(fields):
            if _tab_type is None or tab_type == _tab_type:
                tk.Label(input_frame, text = label, width=25, anchor="e").grid(
                    row=i, column=0, pady=2)
                if field_type == "combo":
                    widget = ttk.Combobox(input_frame, values=args[0], width=25, state="readonly")
                else:
                    widget = ttk.Entry(input_frame, width=25)
                widget.grid(row=i, column=1, pady=5)
                self.tabs_entries[group_id][key] = widget
        
        if group_id != 0:
            self.tabs_entries[group_id]["issue_time"] = self.tabs_entries[0]["issue_time"]

        clouds_frame = tk.LabelFrame(input_frame, text="Облачность", padx=10, pady=10)
        clouds_frame.grid(row=i+1, column=0, columnspan=2)
        self.tabs_entries[group_id]["clouds_entries"] = []

        Button(clouds_frame, text="Добавить", 
               command=lambda frame = clouds_frame: self.add_cloud_row(frame, group_id)).grid(row=2, column=0, columnspan=3)

        self.add_cloud_row(clouds_frame, group_id)

    def add_cloud_row(self, frame, group_id):
        len_clouds_entries = len(self.tabs_entries[group_id]["clouds_entries"])

        cloud_row_frame = tk.LabelFrame(frame, text = f"Группа {len_clouds_entries+1}", pady=5, padx=5)
        cloud_row_frame.grid(row = len_clouds_entries, column=0)

        tk.Label(cloud_row_frame, text = "Облачность", width=12,anchor="n").grid(row=0, column=0, pady=2)
        amount_cb = ttk.Combobox(cloud_row_frame, values = [a["amount"] for a in self.config["clouds_amount"]], width=12)
        amount_cb.grid(row=1, column=0,pady=2)

        tk.Label(cloud_row_frame, text="Высота", width=12, anchor="n").grid(row=0, column=1, pady=2)
        # height_cb = ttk.Entry(cloud_row_frame, width=12)
        height_cb = ttk.Combobox(cloud_row_frame, values = [f"{i:03d}" for i in range(1, 50)], width=5, state="normal")
        height_cb.grid(row=1, column=1, pady=2)

        tk.Label(cloud_row_frame, text="Тип", width=12, anchor="n").grid(row=0, column=2, pady=2)
        type_cb = ttk.Combobox(cloud_row_frame, values = [t["type"] for t in self.config["clouds_type"]], width=12)
        type_cb.grid(row = 1, column= 2, pady=2)

        self.tabs_entries[group_id]["clouds_entries"].append((cloud_row_frame, amount_cb, height_cb, type_cb))

        if len_clouds_entries > 0:
            Button(cloud_row_frame, text="✖", command=lambda frame = cloud_row_frame: self.delete_cloud_row(frame, group_id)).grid(row=0, column=3)

    def delete_cloud_row(self, frame, group_id):
        frame.destroy()
        for entries_list in self.tabs_entries[group_id]["clouds_entries"]:
            if frame in entries_list:
                self.tabs_entries[group_id]["clouds_entries"].remove(entries_list)
                break

    def init_weather_frame(self, tab, group_id):
        weather_frame = tk.LabelFrame(tab, text="Явления", padx=10, pady=10)
        weather_frame.pack(fill="x", padx=10, pady=5)

        weather_container = Frame(weather_frame)
        weather_container.pack(fill="x")

        add_button = Button(weather_frame, text="Добавить явление",
                            command=lambda frame = weather_container : self.add_weather_row(frame, group_id))
        add_button.pack(pady=5)

        self.tabs_entries[group_id]["weather_events"] = []

    def add_weather_row(self, frame, group_id):
        intensities = [x["intensity"] for x in self.config.get("intensity", [])]
        descriptors = [x["descriptor"] for x in self.config.get("descriptor", [])]
        events = [x["event"] for x in self.config.get("weather_events", [])]

        row_frame = Frame(frame)
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
                            command=lambda : self.remove_weather_row(row_frame, group_id))
        remove_btn.grid(row=0, column=3, padx=2)

        self.tabs_entries[group_id]["weather_events"].append((row_frame, cb_int, cb_desc, cb_event))

    def on_tab_switched(self, event):
        selected = event.widget.select()
        tab_index = event.widget.index(selected)

        if event.widget.tab(tab_index, "text") == "+":
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

        Button(new_tab, text="Удалить группу",
            command=lambda tab=new_tab: self.remove_tab(tab)
            ).pack(pady=8)

    def remove_tab(self, tab_frame):
        tabs = list(self.notebook.tabs())

        group_id = self.tab_id_map.pop(tab_frame, None)
        if group_id is not None:
            self.tabs_entries.pop(group_id, None)

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
        
    def remove_weather_row(self, frame, group_id):
        frame.destroy()
        self.tabs_entries[group_id]["weather_events"] = [row for row in self.tabs_entries[group_id]["weather_events"] if row[0] != frame]

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
            _, amount, height, cloud_type = row
            a = amount.get().strip()
            h = height.get().strip()
            c = cloud_type.get().strip()
            if a:
                clouds.append({
                    "amount" : a,
                    "height" : h,
                    "cloud_type" : c 
                })
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

        taf_output = " ".join(generate_taf(data) for data in all_data.values()) + "="


        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, taf_output)

    def init_json_editor(self):
        json_editor = JsonEditor()
        json_editor.mainloop()

    def close_app(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MeteoTafApp(root)
    root.mainloop()