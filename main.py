import queue
import threading
import time

from manager import manager, invia_richiesta
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

    #per ora, elenco dei servizi validi (per evitare di scaricare immagini troppo pesanti sui container accidentalmente)
    servizi_validi = ["alpine", "hello-world"]

    #menu per l'utente così può specificare che servizio vuole fare runnare
    while True:
        comando = input(f"---\nManda un servizio da schedulare ('exit' per uscire): \nServizi disponibili: {servizi_validi}\n")
        #uscita forzata dal programma, senza aspettare che il manager abbia finito con la coda.
        if comando == "exit forzata":
            break
        #uscita "soft" dal programma, aspetta che il manager finisca le richieste in coda prima di chiudersi
        if comando == "exit":
            #blocca l'esecuzione finché il manager non ha finito tutto quello che c'era in coda (tracciato da task_done)
            coda.join()
            break
        if comando not in servizi_validi:
            print("Comando o servizio non disponibile, riprova con uno dei comandi/servizi specificati sopra.")
            continue
        #invia la richiesta all'oggetto "coda", condiviso con il thread manager
        invia_richiesta(coda, comando)
        #per printare di nuovo la richiesta di input dopo l'operazione aspetta 3 secondi (posso sostituirlo dopo con un .join() )
        time.sleep(3)

    print("---Il codice ha finito di eseguire---")

