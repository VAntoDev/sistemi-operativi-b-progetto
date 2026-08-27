#thread heartbeat. Si occupa dela Failure Detection, controlla se un nodo cade + fa il Failover per i suoi container su altri nodi attivi
import time

from config import Config
from manager import invia_richiesta

#controlla lo stato dei nodi, se un nodo cade attiva il failover
def heartbeat(lista_nodi, coda, intervallo=3):
    while True:
        try:
            for nome, nodo in lista_nodi.items():
                #se un nodo è down, allora attiva il failover per spostare i suoi container su altri nodi
                stato_nodo = nodo.is_up()
                if stato_nodo == False:
                    failover(nodo.container_attivi, nodo.nome, coda)
        except Exception as e:
            print(f"Failure_detection> Errore nel thread heartbeat: {e}")
        time.sleep(intervallo)

#questa funzione runna i container che erano sul nodo caduto sugli altri container, passandoli nella coda del manager
def failover(container_attivi_nodo, nome, coda):
    #prende i container che erano attivi sul nodo come copia
    container_attivi = list(container_attivi_nodo)
    container_attivi_nodo.clear()

    #se il nodo NON aveva container attivi, allora non fare nulla
    if len(container_attivi) == 0:
        return

    #se aveva dei container attivi allora ricrea la config e falla deployare al manager
    for container in container_attivi:
        servizio_name = container["nome"].split("-")[0]
        config_ricreata = Config(
            image=container["immagine"],
            #mi serve solo servizio_name, poi quando il manager fa il deploy darà al container un suo uuid univoco
            servizio_name=servizio_name,
            command=container["comando"]
        )
        invia_richiesta(coda, "deploy", config_ricreata)

    print(f"\nFailure_detection> Il nodo {nome} aveva questi task attivi e verranno rischedulati: {container_attivi}")