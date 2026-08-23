import time
import queue
import threading
from docker.errors import DockerException
from nodi import list_nodes, deploy_container
from nodo import Nodo
from utils import is_container_vecchio


#calcola qual è il nodo con meno container attivi attualmente
def trova_nodo_least_loaded(nodi_e_container):
    punteggi = {}
    for nodo, containers in nodi_e_container.items():
        punteggio = len(containers)
        punteggi[nodo] = punteggio
    #ritorna il punteggio minimo tra i punteggi salvati nel dizionario,
    #il nodo con il punteggio minore è quello con meno container attivi
    #se due hanno punteggi uguali, sceglie il primo nella lista
    return min(punteggi, key=lambda punteggio_nodo: punteggi[punteggio_nodo])

#rimuove i container spenti su un nodo
def rimuovi_container_spenti(node):
    rimossi = []
    for container in node.client.containers.list(all=True):
        #se il container ha come status exited o dead, è spento
        spento = container.status in ("exited", "dead")
        #nel caso in cui sia in status di created non sta eseguendo, ma potrebbe passare da created -> up, quindi
        #controllo che sia più vecchio di una certa soglia di minuti prima di eliminarlo
        bloccato = container.status == "created" and is_container_vecchio(container, 1)

        #se è spento o bloccato, allora viene eliminato
        if spento or bloccato:
            tags = container.image.tags
            immagine = tags[0] if tags else "nessun tag"
            nome = f"{container.name}, {immagine}"
            try:
                container.remove()
                rimossi.append(nome)
            except (DockerException, Exception) as e:
                print(f"Errore rimuovendo {nome}: {e}")
    if rimossi: #se rimossi ha elementi allora runna il print, altrimenti no perché non ci sono stati container da rimuovere
        print(f"Container già spenti rimossi su {node.nome}: {rimossi}")
    return rimossi

#data una lista di nodi, su ognuno di essi esegue "rimuovi_container_spenti" se è attivo
def rimuovi_container_spenti_tutti_nodi(lista_nodi):
    for nome, nodo in lista_nodi.items():
        stato = nodo.is_up()
        if stato: # se il nodo è attivo, allora rimuovi i container spenti al suo interno
            rimuovi_container_spenti(nodo)
        else:
            print(f"{nome} è down, salto la pulizia")

#prende i nodi e le informazioni sui loro container per schedulare un servizio sul nodo least loaded
def schedula_servizio(config, lista_nodi, lista_nodi_stats):
    #imposta le configurazioni con cui verrà runnato il container
    config_diz = {
        "image": config.image,
        "command": config.command,
        "name": config.name,
        "detach": True, #Sempre True, i container devono runnare in background
    }

    #calcola il nodo least loaded e salva il risultato
    nodo_least_loaded = trova_nodo_least_loaded(lista_nodi_stats)

    #esegue il container nel nodo con meno container attivi
    deploy_container(lista_nodi[nodo_least_loaded], config_diz)

#usata per inviare una richiesta al manager
def invia_richiesta(coda, servizio):
    #mette un oggetto nella coda in modo atomico grazie ad un lock interno, questo evita le race condition
    coda.put(servizio)
    #print(f"Richiesta '{servizio.get_name()}' aggiunta alla coda")

#ciclo che il nodo manager ripete per eseguire le richieste che gli vengono mandate dall'utente
def manager(lista_nodi, coda):
    while True:
        try:
            #prende dalla coda una richiesta, se non c'è nessuna richiesta va in queue.empty -> pass
            #aspetta fino a 1 secondo per una nuova richiesta e ne gestisce una per volta, poi ricontrolla
            richiesta = coda.get(timeout=1)
            print(f"Manager> Schedulo ==> ", end="")
            richiesta.stampa_config()
            #schedula il servizio sul nodo least loaded
            schedula_servizio(richiesta, lista_nodi, list_nodes(lista_nodi))

            list_nodes(lista_nodi, stampa=True)
            #segnala che questa richiesta è stata soddisfatta, quindi attiva il join()
            coda.task_done()
        #se la coda è vuota, fai altro (questo forse lo modificherò in seguito, magari in un altro thread)
        except queue.Empty:
            rimuovi_container_spenti_tutti_nodi(lista_nodi)
            pass  #nessuna richiesta in coda,continua il ciclo

        #aspetta un secondo per fare una richiesta
        time.sleep(1)