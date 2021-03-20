# Bitte alles mit Kommentaren versehen, damit jeder weiß was im Code passiert


# Imports
import psutil as psu
import matplotlib.pyplot as plt
import time

# Probier Klasse --> kann gelöscht werden, wenn wir das nicht brauchen
class Test():

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
        plt.xlabel('frequency in Mhz')
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
        plt.xlabel('workload in %')
        plt.xlabel('time in s')

        # Schleife
        while True:
            for c, i in enumerate(psu.cpu_percent(percpu=True)):
                y[c] = i
            sub.bar(x, y, align="center", color="blue")
            fig.canvas.draw()
            fig.canvas.flush_events()
