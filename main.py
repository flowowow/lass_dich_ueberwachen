# Bitte alles mit Kommentaren versehen, damit jeder weiß was im Code passiert


# Imports
import psutil as psu
import matplotlib.pyplot as plt
import pandas as pd
import time
import math
# Kivy imports
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.snackbar import Snackbar
from kivy.uix.widget import WidgetException


# Übergreifende Variablen
processes_objs_list = []
processes_names_list = {}


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


class Application(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kv = Builder.load_file("KV.kv")
        self.running_processes, self.stopped_processes = self.get_processes()
        self.snack = Snackbar(text="Select Applications to track")
    
    def build(self):
        return self.kv

    def on_start(self):
        self.create_list()
    
    def create_list(self) -> None:
        for c, i in enumerate(self.running_processes):
            processes_objs_list.append(ListItem(text=i))
            processes_names_list[processes_objs_list[c].text] = False
            self.root.ids.processes.add_widget(processes_objs_list[c])

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
    # Auch das try-except ist echt hässlig. Wär geil wenn das noch schöner wird
    def select_item(self, instance) -> None:
        try:
            for i in processes_objs_list:
                if i.text == instance.text:
                    if i.icon == "checkbox-blank-outline":
                        i.icon = "checkbox-marked-outline"
                        processes_names_list[i.text] = True
                    elif i.icon == "checkbox-marked-outline":
                        i.icon = "checkbox-blank-outline"
                        processes_names_list[i.text] = False
        except AttributeError:
            for i in processes_objs_list:
                if i.text == instance.parent.parent.text:
                    if i.icon == "checkbox-blank-outline":
                        i.icon = "checkbox-marked-outline"
                        processes_names_list[i.text] = True
                    elif i.icon == "checkbox-marked-outline":
                        i.icon = "checkbox-blank-outline"
                        processes_names_list[i.text] = False

    def activate_spinner(self, instance):
        boolean = True

        for i in processes_names_list:
            if processes_names_list[i]:
                boolean = True
                break
        else:
            boolean = False
            try:
                self.snack.show()
            except WidgetException:
                pass
        
        if boolean:
            if instance.md_bg_color == self.theme_cls.primary_color:
                instance.icon = "stop"
                instance.md_bg_color = (.79, .22, .29, 1)
            else:
                instance.md_bg_color = self.theme_cls.primary_color
                instance.icon = "play"

            for c, i in enumerate(self.root.walk()):
                if c == 7:
                    if not i.active:
                        i.active = True
                    elif i.active:
                        i.active = False


class ListItem(OneLineIconListItem):
    icon = StringProperty("checkbox-blank-outline")

    def on_press(self):
        super().on_press()
        Application.select_item(Application, self)


Application().run()