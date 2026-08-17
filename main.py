from nodi import crea_client, list_nodes, deploy_container, stop_container
from utils import scelta_deploy_container, scelta_stop_container, scelta_remove_container
import time

if __name__ == '__main__':
    #creo un dizionario con i nodi disponibili:
    lista_nodi = {
        "nodo1": crea_client("172.21.0.2", 3),
        "nodo2": crea_client("172.21.0.3", 3),
        "nodo3": crea_client("172.21.0.4", 3),
    }
    #time.sleep(1)

    #lista i nodi e il loro stato attuale, con i container che stanno runnando attualmente
    lista_nodi_containers = list_nodes(lista_nodi)

    #DEPLOY CONTAINER, fa scegliere all'utente un container da deployare su un nodo
    scelta_deploy_container(lista_nodi["nodo2"])

    lista_nodi_containers = list_nodes(lista_nodi)

    #STOP CONTAINER, ferma un container in un nodo in base alla scelta dell'utente
    scelta_stop_container(lista_nodi, lista_nodi_containers)

    #RIMUOVI CONTAINER, rimuove un container in un nodo in base alla scelta dell'utente
    lista_spenti_accesi_nodi_containers = list_nodes(lista_nodi, True)
    scelta_remove_container(lista_nodi, lista_spenti_accesi_nodi_containers)

    print("---Il codice ha finito di eseguire---")

