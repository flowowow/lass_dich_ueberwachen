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

    # Endlose Schleife die in jeder Wiederholung die aktuelle CPU Auslastung ans Ende eines Graphen malt
    def cpu_stats(self) -> None:
        # Variablen deklarieren
        start_time = time.time()
        y = [0]
        x = [0]

        # Graph vorzeichnen und betiteln
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot([1], y, color="blue")
        plt.title('CPU Workload')
        plt.xlabel('workload in %')
        plt.xlabel('time in s')

        # Schleife
        while True:
            y.append(psu.cpu_percent())
            x.append(round(time.time() - start_time, 2))
            ax.plot(x, y, color="blue")
            fig.canvas.draw()
            fig.canvas.flush_events()


Test.cpu_stats(Test)