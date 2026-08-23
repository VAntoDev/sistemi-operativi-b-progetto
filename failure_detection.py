#in questo file ci sono la Failure Detection tramite Heartbeat per controllare se un nodo cade + il Failover per i suoi container su altri nodi attivi
import threading
import time

from manager import invia_richiesta
from nodo import Nodo

stato_nodi = {}

#controlla lo stato dei nodi, se un nodo cade attiva il failover
def heartbeat(lista_nodi, coda, intervallo=5):
    while True:
        for nome, nodo in lista_nodi.items():
            stato_nodi[nome] = nodo.is_up()
            if stato_nodi[nome] == False:
                failover(nodo.container_attivi, nodo.nome, coda)
        #print(stato_nodi)
        time.sleep(intervallo)

#questa funzione runna i container che erano sul nodo caduto sugli altri container, passandoli nella coda del manager
def failover(container_attivi_nodo, nome, coda):
    #creo una copia dei container attivi, in questo modo posso subito fare clear della lista e non rischedula quei container attivi di nuovo
    container_attivi = list(container_attivi_nodo)
    #clear della lista
    container_attivi_nodo.clear()
    if len(container_attivi)==0:
        #print("Il nodo non aveva container attivi, non sposto nulla")
        return

    #se il container era nella lista container attivi allora manda una richiesta al manager di rischedularlo
    for container in container_attivi:
        invia_richiesta(coda, container["immagine"])
    print("Il nodo " + f'{nome}' + " aveva questi container attivi e verranno rischedulati: ", container_attivi)