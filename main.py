import queue
import threading
import time

import failure_detection
from config import Config
from manager import manager, invia_richiesta
from menu import Menu
from nodi import list_nodes, deploy_container, stop_container
from nodo import Nodo
from utils import scelta_deploy_container, scelta_stop_container, scelta_remove_container

if __name__ == '__main__':
    #creo un oggetto Nodo per ogni nodo del cluster,
    #l'attributo "client" è un oggetto DockerClient che viene usato per comunicare con quel nodo
    lista_nodi = {
        "nodo1": Nodo("nodo1", "172.21.0.2"),
        "nodo2": Nodo("nodo2", "172.21.0.3"),
        "nodo3": Nodo("nodo3", "172.21.0.4"),
    }

    #l'oggetto "queue" è una coda thread-safe, in questo modo posso usare una risorsa condivisa tra i thread
    #senza preoccuparmi di incappare in una race condition
    coda = queue.Queue()

    #creo un thread separato per il manager, uso "daemon=True" così il thread continua a eseguire in background mentre
    #questo thread continua a eseguire
    thread_manager = threading.Thread(target=manager, args=(lista_nodi, coda), daemon=True)
    #avvio il thread
    thread_manager.start()

    #creo un thread che si occupa di controllare se i nodi sono caduti per gestire il problema
    thread_failure_detection = threading.Thread(target=failure_detection.heartbeat, args=(lista_nodi, coda, 5), daemon=True)
    thread_failure_detection.start()

    #per ora, elenco dei servizi validi (per evitare di scaricare immagini troppo pesanti sui container accidentalmente)
    servizi_validi = [
        Config("alpine", "sleep infinity"),
        Config(image="hello-world")
    ]

    menu = Menu(lista_nodi, coda, servizi_validi)
    menu.avvia_menu()

    print("---Il codice ha finito di eseguire---")

