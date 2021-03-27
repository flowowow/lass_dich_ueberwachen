# Bitte alles mit Kommentaren versehen, damit jeder weiß was im Code passiert


# Imports
# python -m pip install module --> universeller Installations Command
import threading
# Bitte lieber Multiprocessing anstatt Threading benutzen
import multiprocessing
import psutil as psu
import matplotlib.pyplot as plt
import pandas as pd
import os.path
import time
import math
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.widget import WidgetException


# Globale Variablen
interval = 4


# Probier Klasse --> kann gelöscht werden, wenn wir das nicht brauchen
# Wird zu Zeit auch nicht verwendet
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


# MDSwitch wäre hier auf jeden Fall passender --> könnte man mit custom Klasse implementieren
# Wie eine .kv Datei, bloß als string
# https://kivy.org/doc/stable/guide/lang.html für mehr Info
# https://kivy.org/doc/stable/api-kivy.lang.builder.html?highlight=builder# für mehr Info zum Builder
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
        # Läd .kv Datei
        # https://kivy.org/doc/stable/api-kivy.lang.builder.html?highlight=builder# für mehr Info
        self.kv = Builder.load_file("KV.kv")
        self.filtered = True
        self.running_processes, self.stopped_processes = self.get_processes(False)
        self.tracking = False
        # Snackbar Objekt
        # https://kivymd.readthedocs.io/en/0.104.0/components/snackbar/index.html für mehr Info
        self.snack1 = Snackbar(text="Select applications to track")
        self.snack2 = Snackbar(text="Turn off tracking to select/deselect applications")
        self.processes_objs_list = []
        self.processes_names_dict = {}
    
    # build() wird nach __init__() zum Programmstart ausgeführt
    def build(self):
        # Icons werden nicht angezeigt
        # Das Popup Menu ist hässlig formatiert, ich kriegs aber einfach nicht besser hin :(
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "icon": "filter-outline",
                "text": "Filtered"
            }, 
            {
                "viewclass": "OneLineListItem",
                "icon": "format-list-bulleted",
                "text": "Everything"
            }]
        # Position des Symbols in Toolbar wird nicht aktualisiert, wenn die Fenstergröße verstellt wird --> fix
        # Dropdown Menü Objekt
        # https://kivymd.readthedocs.io/en/0.104.0/components/dropdown-item/index.html für mehr Info
        self.filter_menu = MDDropdownMenu(items=menu_items, width_mult=3.5, caller=self.kv.ids.toolbar.children[0], callback=self.filter_menu_close)
        return self.kv

    # on_start wird nach build() zum Programmstart ausgeführt
    def on_start(self):
        self.create_list()
    
    # Für jeden laufenden Process wird ein Listenobjekt erstellt
    def create_list(self) -> None:
        self.processes_objs_list = []
        for c, i in enumerate(self.running_processes):
            # Läd String im .kv Format
            item = Builder.load_string(LIST_ITEM)
            item.text = i
            self.processes_objs_list.append(item)
            self.processes_names_dict[i] = False
            # Objekt wird mit ID gesucht und zum Renderer hinzugefügt
            self.root.ids.processes.add_widget(self.processes_objs_list[c])

    # Gibt zwei Dictionaries zurück, die alle zur Zeit laufenden und gestoppten Prozesse beinhalten
    # key --> name
    # value --> pid
    def get_processes(self, force_unfiltered_processes) -> dict:
        # Das hier muss weg!
        if force_unfiltered_processes:
            self.filtered = False

        running_processes = {}
        stopped_processes = {}
        # Geht hier bitte nochmal drüber. Ich hab lediglich geschätzt was Windows sein könnte und was nicht
        # Liste an Prozessen die rausgefiltert werden
        windows_processes = ["System Idle Process", "System", "RuntimeBroker.exe", "Registry", "svchost.exe", "smss.exe", "lsass.exe",
                            "services.exe", "csrss.exe", "fontdrvhost.exe", "wininit.exe", "AppVShNotify.exe", "MemCompression", "powershell.exe",
                            "UserOOBEBroker.exe", "spoolsv.exe", "RtkAudUService64.exe", "MoUsoCoreWorker.exe", "nvcontainer.exe", "SafeConnect.ServiceHost.exe",
                            "MsMpEng.exe", "SgrmBroker.exe", "dasHost.exe", "sihost.exe", "NisSrv.exe", "CompPkgSrv.exe", "GoogleCrashHandler.exe", 
                            "GoogleCrashHandler64.exe", "taskhostw.exe", "YourPhoneServer.exe", "dllhost.exe", "conhost.exe", "SearchIndexer.exe", "dwm.exe",
                            "McCSPServiceHost.exe", "SecurityHealthService.exe", "SettingSyncHost.exe", "ctfmon.exe", "StartMenuExperienceHost.exe",
                            "nvsphelper64.exe", "SearchProtocolHost.exe", "SearchFilterHost.exe", "winlogon.exe", "audiodg.exe", "SecurityHealthSystray.exe",
                            "SystemSettingsBroker.exe", "ApplicationFrameHost.exe", "TextInputHost.exe", "WmiPrvSE.exe"]

        # Iteriert durch alle laufenden Prozesse
        # Wenn self.filter == True --> werden nur die Prozesse angezeigt, die nicht in windows_processes sind
        # self.filter wird in __init__() deklariert und in filter_menu_close() verändert
        for process in psu.process_iter():
            if not self.filtered or not process.name() in windows_processes:
                if process.status() == "running":
                    # unnötige .exe Endung wird vom Anwendungsnamen entfernen
                    name = process.name().split(".exe")[0]
                    running_processes[name] = process.pid
                elif process.status() == "stopped":
                    name = process.name().split(".exe")[0]
                    stopped_processes[name] = process.pid

        return running_processes, stopped_processes

    # Der For-Loop hier funktioniert, ist aber ziemlich ineffizient --> bessere Lösung?
    # Vielleicht sollte dieses System auch generell nochmal überholt werden
    # Wird aufgerufen wenn ein Listenobjekt gedrückt wird
    # Ändert Symbol des Listenobjekts und setzt ausgewählten Prozess in Dict auf True
    def select_item(self, instance, position) -> None:
        # Schaut ob Tracking bereits läuft
        if not self.tracking:
            # Überprüft durch extra Parameter welches Objekt die Funktion aufgerufen hat
            # Je nach instance wird entweder Eltern Objekt oder Kind Objekt für Symbol oder Text Änderungen verwendet
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
        # Wenn Tracking läuft, wird Fehlermeldung über Snackbar angezeigt
        # https://kivymd.readthedocs.io/en/0.104.0/components/snackbar/index.html für mehr Info
        else:
            try:
                self.snack2.show()
            # Bringt Ausnahme hervor, wenn die Snackbar bereits angezeigt wird
            except WidgetException:
                pass

    # Wird ausgeführt wenn der Start Knopf gedrückt wird
    # Ändert Symbol und Farbe des Knopfes, sowie eine boolean
    def activate_tracking(self, instance):
        block_action = True

        # Wenn keins der Listenobjekte ausgewählt wurde, wird eine Snackbar mit Warnung angezeigt, 
        # Sowie die weiteren Änderungen übersprungen
        for i in self.processes_names_dict:
            if self.processes_names_dict[i]:
                block_action = False
                break
        else:
            block_action = True
            # Snackbar
            # https://kivymd.readthedocs.io/en/0.104.0/components/snackbar/index.html für mehr Info
            try:
                self.snack1.show()
            # Bringt Ausnahme hervor, wenn die Snackbar bereits angezeigt wird
            except WidgetException:
                pass
        
        if not block_action:
            # Überprüft anhand der Farbe des Knopfes, ob Tracking läuft oder nicht
            # Das ist etwas gay, funktioniert aber
            if instance.md_bg_color == self.theme_cls.primary_color:
                # boolean = True
                self.tracking = True
                # Symbol des Knopfes ändern
                instance.icon = "stop"
                # Farbe des Knopfes ändern (prozentualer rbga Wert als Dezimalzahl)
                instance.md_bg_color = (.79, .22, .29, 1) # --> Rot
            else:
                # boolean = False
                self.tracking = False
                # Symbol des Knopfes ändern
                instance.icon = "play"
                # Farbe des Knopfes ändern (standard Farbe)
                instance.md_bg_color = self.theme_cls.primary_color # --> Blau

    # Läd die Liste an Prozessen neu
    def refresh_processes_list(self):
        self.root.ids.processes.clear_widgets()
        self.running_processes, self.stopped_processes = self.get_processes(False)
        self.create_list()


    # Schließt Dropdown Menü und setzt eine bool auf True oder False
    def filter_menu_close(self, instance):
        if instance.text == "Filtered":
            self.filtered = True
            self.refresh_processes_list()
        elif instance.text == "Everything":
            self.filtered = False
            self.refresh_processes_list()
        # MDDropdownMenu.dismiss() schließt das Dropdown Menü
        # https://kivymd.readthedocs.io/en/0.104.0/components/dropdown-item/index.html für mehr Info
        self.filter_menu.dismiss()


# Speichert alle laufenden Prozesse und deren Laufzeit als .xlsx ab.
# Eine Iteration der While Schleife braucht auf meinem (Flos) Rechner etwa 0,45s. 
# time.sleep() wartet zur Zeit 4s
def tracking():
    start_time = time.time()
    interval_length = 0
    # Das überprüft, ob sich im gleichen Verzeichnis wo auch das Skript liegt eine .xlsx Datei befindet. 
    # Falls ja, wird sie ausgelesen, falls nicht, wird sie erstellt
    if not os.path.isfile("processes.xlsx"):
        all_processes_df = pd.DataFrame()
        all_processes_df.to_excel("processes.xlsx")
    else:
        all_processes_df = pd.read_excel("processes.xlsx")

    while True:
        # time.sleep() ist doch besser als eine Kondition, da dadurch ein enormer Teil an Rechenleistung erspart bleibt @Aaron
        time.sleep(interval)
        running_processes, stopped_processes = Application.get_processes(Application, True)
        # Hier wird überprüft, ob im Moment Prozesse laufen, die noch nicht in der Datei hinterlegt sind.
        # Falls ja, werden alle fehlenden Prozesse hinzugefügt. Falls nein, wird die Laufzeit aller Prozesse ausgelesen
        # Und die Länge der letzten Iteration dazu addiert
        for i in running_processes:
            if not i in all_processes_df.columns:
                all_processes_df[i] = [0.0]
            else:
                all_processes_df.loc[0, i] += interval_length
        # Intervalllänge und Startzeit werden zurückgesetzt
        interval_length = time.time() - start_time
        start_time = time.time()
        # Anschließend wird die Datei gespeichert
        all_processes_df.to_excel("processes.xlsx", index=False)
        

# Mit Threading ruckelt das UI, wenn die While Schleife in tracking() durchläuft
# Multiprocessing wäre hier besser, hab es aber bislang noch nicht implementieren können ~Flo

# Threading erlaubt es, mehrere Prozesse gleichzeitig laufen zu lassen
# So werden hier UI und tracking() Funktion parallel gestartet
# Mehr zu Threading hier: https://www.geeksforgeeks.org/multithreading-python-set-1/

# Application().run() führt Application Klasse aus
# Klasse akzeptiert beim Aufruf keine Argumente und gibt eine neue Instanz ohne Features zurück,
# die keine Instanzattribute hat und keine annehmen kann.
# https://kivy.org/doc/stable/api-kivy.app.html für mehr Info
threading.Thread(target=tracking, name="Lass Dich Ueberwachen").start()
threading.Thread(target=Application().run(), name="Lass Dich Ueberwachen UI").start()