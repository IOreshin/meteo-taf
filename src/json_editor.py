
from loader import load_config
import tkinter as tk
from tkinter import ttk
from tkinter import ttk, Button, Label

class JsonEditor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("JSON Editor")
        self.config = load_config()
        self.combobox_values = ["Общие",
                                "По коду"]

        self.init_ui()


    def init_ui(self):
        self.part_frame = tk.LabelFrame(self, text="Редактирование условий", padx=10, pady=10)
        self.part_frame.grid(row=0, column=0)
        
        Label(self.part_frame, text="Раздел").grid(row=0,column=0, padx=5, pady=5)
        self.part_combobox = ttk.Combobox(self.part_frame, 
                                          values=self.combobox_values)
        self.part_combobox.current(0)
        self.part_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.part_combobox.bind("<<ComboboxSelected>>", self.on_combobox_select)

        self.condition_frame = tk.LabelFrame(self, text="Редактирование общих правил", padx=10, pady=10)
        self.condition_frame.grid(row=1, column=0)
        Button(self.condition_frame, text="Кнопка").grid(row=0, column=0)

    def init_conditions_frame(self, frame_type):
        match frame_type:
            case "Общие":
                self.condition_frame.configure(text="Редактирование общих правил")
                pass
            case "По коду":
                self.condition_frame.configure(text="Редактирование правил по коду")
                pass



    def on_combobox_select(self, event):
        self.init_conditions_frame(self.part_combobox.get())


if __name__=="__main__":
    JsonEditor().mainloop()