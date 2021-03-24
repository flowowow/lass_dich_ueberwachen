# Bitte alles mit Kommentaren versehen, damit jeder weiß was im Code passiert


# Imports
import psutil as psu
import matplotlib.pyplot as plt
import pandas as pd
import time
import math
# "pip install kivy" und "pip install kivymd" zum Importieren
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.widget import WidgetException



# Probier Klasse --> kann gelöscht werden, wenn wir das nicht brauchen
class Test():

    # Endlose Schleife die in jeder Wiederholung die aktuelle Takt Frequenz der CPU ans Ende eines Graphen malt
    def cpu_freq(self) -> None:
        # Variablen deklarieren
        start_time = time.time()
        y = [0]
        x = [0]

        # Graph vorzeichnen und betiteln
        plt.ion()
        fig = plt.figure()
        sub = fig.add_subplot(111)
        sub.plot([1], y, color="blue")
        plt.title('CPU Frequency')
        plt.ylabel('frequency in Mhz')
        plt.xlabel('time in s')

        # Schleife
        while True:
            y.append(psu.cpu_freq().current)
            x.append(round(time.time() - start_time, 2))
            sub.plot(x, y, color="blue")
            fig.canvas.draw()
            fig.canvas.flush_events()

    # Endlose Schleife die in jeder Wiederholung die CPU Auslastung in einem Balkendiagramm aktualisiert
    def cpu_perc(self) -> None:
        # Variablen deklarieren
        x = []
        y = []
        for i in range(psu.cpu_count()):
            x.append(i + 1)
            y.append(0)
        
        # Graph vorzeichnen und betiteln
        plt.ion()
        fig = plt.figure()
        sub = fig.add_subplot(111)
        sub.bar(x, y, align="center", color="blue")
        plt.title('CPU Workload')
        plt.xlabel('cores')
        plt.ylabel('workload in %')

        # Schleife
        while True:
            for c, i in enumerate(psu.cpu_percent(percpu=True)):
                y[c] = i
            sub.bar(x, y, align="center", color="blue")
            fig.canvas.draw()
            fig.canvas.flush_events()
    
    # Identisch zu cpu_freq(), bloß mit Prozentzahl und separatem Graphen für jeden Thread
    def cpu_perc_all_cores(self):
        start_time = time.time()
        x = [0]
        y = [[0]]
        subs = []

        plt.ion()
        fig = plt.figure()
        plt.title('CPU Workload')

        for i in range(psu.cpu_count()):
            y.append([0])
            subs.append(fig.add_subplot(math.ceil(psu.cpu_count() / 4), 4, i + 1))
            subs[i].plot(x, y[i], color="blue")

        while True:
            x.append(round(time.time() - start_time, 2))
            for c, i in enumerate(psu.cpu_percent(percpu=True)):
                y[c].append(i)
                subs[c].plot(x, y[c], color="blue")
            fig.canvas.draw()
            fig.canvas.flush_events()


# Wie eine .kv Datei, bloß als string
LIST_ITEM = """
OneLineIconListItem:
    on_press: app.select_item(self, "OneLineIconListItem")

    IconLeftWidget:
        icon: "checkbox-blank-outline"
        on_press: app.select_item(self, "IconLeftWidget")
"""

# App Klasse
class Application(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kv = Builder.load_file("KV.kv")
        self.running_processes, self.stopped_processes = self.get_processes()
        self.tracking = False
        self.snack1 = Snackbar(text="Select applications to track")
        self.snack2 = Snackbar(text="Turn off tracking to select/deselect applications")
        self.processes_objs_list = []
        self.processes_names_dict = {}
    
    def build(self):
        # Icons werden nicht angezeigt
        menu_items = [{"icon": "filter-outline", "text": "Filtered"}, {"icon": "format-list-bulleted", "text": "Everything"}]
        # Position des Symbols in Toolbar wird nicht aktualisiert, wenn die Fenstergröße verstellt wird --> fix
        self.filter_menu = MDDropdownMenu(items=menu_items, width_mult=3.5, caller=self.kv.ids.toolbar.children[0], callback=self.filter_menu_close)
        return self.kv

    def on_start(self):
        self.create_list()
    
    # Für jeden laufenden Process wird ein Listenobjekt erstellt
    def create_list(self) -> None:
        for c, i in enumerate(self.running_processes):
            item = Builder.load_string(LIST_ITEM)
            item.text = i
            self.processes_objs_list.append(item)
            self.processes_names_dict[i] = False
            self.root.ids.processes.add_widget(self.processes_objs_list[c])

    # Gibt zwei Dictionaries zurück, die alle zur Zeit laufenden und gestoppten Prozesse beinhalten
    # key --> name
    # value --> pid
    def get_processes(self) -> dict:
        running_processes = {}
        stopped_processes = {}

        for process in psu.process_iter():
            if process.status() == "running":
                running_processes[process.name()] = process.pid
            elif process.status() == "stopped":
                stopped_processes[process.name()] = process.pid

        return running_processes, stopped_processes

    # Der For-Loop hier funktioniert, ist aber ziemlich ineffizient --> bessere Lösung?
    # Wird aufgerufen wenn ein Listenobjekt gedrückt wird
    def select_item(self, instance, position) -> None:
        if not self.tracking:
            if position == "IconLeftWidget":
                for i in self.processes_objs_list:
                    if i.text == instance.parent.parent.text:
                        if instance.icon == "checkbox-blank-outline":
                            instance.icon = "checkbox-marked-outline"
                            self.processes_names_dict[i.text] = True
                        elif instance.icon == "checkbox-marked-outline":
                            instance.icon = "checkbox-blank-outline"
                            self.processes_names_dict[i.text] = False
            elif position == "OneLineIconListItem":
                for i in self.processes_objs_list:
                    if i.text == instance.text:
                        if instance.children[0].children[0].icon == "checkbox-blank-outline":
                            instance.children[0].children[0].icon = "checkbox-marked-outline"
                            self.processes_names_dict[i.text] = True
                        elif instance.children[0].children[0].icon == "checkbox-marked-outline":
                            instance.children[0].children[0].icon = "checkbox-blank-outline"
                            self.processes_names_dict[i.text] = False
        else:
            try:
                self.snack2.show()
            except WidgetException:
                pass

    # Wird ausgeführt wenn der Start Knopf gedrückt wird
    def activate_tracking(self, instance):
        boolean = True

        for i in self.processes_names_dict:
            if self.processes_names_dict[i]:
                boolean = True
                break
        else:
            boolean = False
            try:
                self.snack1.show()
            except WidgetException:
                pass
        
        if boolean:
            if instance.md_bg_color == self.theme_cls.primary_color:
                self.tracking = True
                instance.icon = "stop"
                instance.md_bg_color = (.79, .22, .29, 1)
            else:
                self.tracking = False
                instance.icon = "play"
                instance.md_bg_color = self.theme_cls.primary_color

    def filter_menu_close(self, instance):
        print(instance.text)
        self.filter_menu.dismiss()


Application().run()