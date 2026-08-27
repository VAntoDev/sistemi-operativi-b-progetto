#thread Manager, si occupa di avviare le azioni che possono essere messe in coda: deploy, scale_down, drain_nodo, attiva_nodo
import time
import queue
import uuid

from docker.errors import DockerException

from config import Config
from cluster import list_nodes, deploy_container, stop_container
from nodo import Nodo

from utils import is_container_vecchio

#calcola qual è il nodo con meno container attivi attualmente
def trova_nodo_least_loaded(lista_nodi, nodi_e_container):
    punteggi = {}
    for nodo, containers in nodi_e_container.items():
        if lista_nodi[nodo].disponibile:
            punteggio = len(containers)
            punteggi[nodo] = punteggio
    #nel caso in cui nessun nodo sia acceso la variabile è vuota e il min() darebbe errore
    if not punteggi:
        return None

    #ritorna il punteggio minimo tra i punteggi salvati nel dizionario,
    #il nodo con il punteggio minore è quello con meno container attivi
    #se due hanno punteggi uguali, sceglie il primo nella lista
    return min(punteggi, key=lambda punteggio_nodo: punteggi[punteggio_nodo])

#calcola qual è il nodo con più container attivi attualmente
def trova_nodo_most_loaded(nodi_e_container):
    punteggi = {}
    for nodo, containers in nodi_e_container.items():
        punteggio = len(containers)
        punteggi[nodo] = punteggio
    #nel caso in cui nessun nodo sia acceso la variabile è vuota e il max() darebbe errore
    if not punteggi:
        return None

    #ritorna il punteggio massimo tra i punteggi salvati nel dizionario
    return max(punteggi, key=lambda punteggio_nodo: punteggi[punteggio_nodo])

#disattiva un nodo, passando i suoi container sugli altri nodi senza che debba essere fermato
def disattiva_svuota_nodo(nome_nodo, lista_nodi, coda):
    #prendo il nodo dalla lista
    nodo = lista_nodi[nome_nodo]
    #da adesso, il nodo non può più ricevere nuovi container da deployare
    nodo.disponibile = False

    #prendo le statistiche dei container su quel nodo
    lista_nodi_stats = list_nodes(lista_nodi)
    #prendo i container da spostare
    containers_da_spostare = lista_nodi_stats.get(nome_nodo, [])

    #per ogni container invio una richiesta di schedulazione, così verranno distribuiti sugli altri nodi
    for container in containers_da_spostare:
        servizio_name = container["nome"].split("-")[0]
        config_ricreata = Config(
            image=container["immagine"],
            servizio_name=servizio_name,
            command=container.get("comando")
        )
        invia_richiesta(coda, "deploy", config_ricreata)
        #ferma il container attuale, ora che è stato schedulato per essere deployato dal manager su altri nodi
        stop_container(nodo, container["id"])

    print(f"\nManager> Nodo {nome_nodo} svuotato: {len(containers_da_spostare)} task rischedulati altrove.")

def attiva_nodo(nome_nodo, lista_nodi):
    lista_nodi[nome_nodo].disponibile = True
    print(f"\nManager> Nodo {nome_nodo} attivato, torna a poter ricevere nuovi task.")

#rimuove i container spenti su UN nodo
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
                print(f"Manager> Errore rimuovendo {nome}: {e}")
    if rimossi: #se rimossi ha elementi allora runna il print, altrimenti no perché non ci sono stati container da rimuovere
        print(f"Manager> Task già spenti rimossi su {node.nome}: {rimossi}")
    return rimossi

#data una lista di nodi, su ognuno di essi esegue "rimuovi_container_spenti" se è attivo
def rimuovi_container_spenti_tutti_nodi(lista_nodi):
    for nome, nodo in lista_nodi.items():
        stato = nodo.is_up()
        #rimuove i container spenti solo se il nodo è attivo
        if stato:
            rimuovi_container_spenti(nodo)
        else:
            #print(f"{nome} è down, salto la pulizia")
            continue

#prende i nodi e le informazioni sui loro container per schedulare un servizio sul nodo least loaded
def schedula_servizio(config, lista_nodi, lista_nodi_stats):
    #crea ID univoco per il container, bassissima possibilità che due container abbiano nomi uguali ma può succedere
    nome_container = f"{config.servizio_name}-{uuid.uuid4().hex[:10]}"

    #imposta le configurazioni con cui verrà runnato il container
    config_diz = {
        "image": config.image,
        "command": config.command,
        "name": nome_container,
        "detach": True, #Sempre True, i container devono runnare in background
    }

    #calcola il nodo least loaded e salva il risultato
    nodo_least_loaded = trova_nodo_least_loaded(lista_nodi, lista_nodi_stats)

    #se trova_nodo_least_loaded ha ritornano None vuol dire che nessun nodo era attivo
    if nodo_least_loaded is None:
        print("Manager> Nessun nodo disponibile per il deploy.")
        return
    #esegue il container nel nodo con meno container attivi
    deploy_container(lista_nodi[nodo_least_loaded], config_diz)

#ritorna solo i nodi + containers dei nodi che contengono quello specifico servizio
def nodi_con_servizio(servizio, lista_nodi_stats):
    nodi_stats_con_servizio = {}
    #controlla in tutti i nodi e in ogni container
    for nome, containers in lista_nodi_stats.items():
        for container in containers:
            #controlla se il nome inizia con quello del servizio desiderato
            if container["nome"].startswith(servizio.servizio_name):
                #se quel container ha quel nome, allora quel servizio è su questo nodo quindi aggiungilo
                #ai nodi che contengono questo servizio
                nodi_stats_con_servizio[nome] = containers
                break
    #ritorna lista dei nodi che hanno il servizio specificato
    return nodi_stats_con_servizio

#fa lo stop di un servizio, verrà rimosso dal manager successivamente
def spegni_servizio(servizio, lista_nodi, lista_nodi_stats):
    #controlla quali nodi hanno quel servizio
    nodi_stats_con_servizio = nodi_con_servizio(servizio, lista_nodi_stats)

    #se nessun nodo ha quel servizio, allora fermati
    if not nodi_stats_con_servizio:
        print(f"Manager> Nessun nodo ha repliche attive di '{servizio.servizio_name}'")
        return

    #trova il nodo most_loaded SOLO tra i nodi che contengono quel servizio
    nodo_most_loaded = trova_nodo_most_loaded(nodi_stats_con_servizio)

    #se trova_nodo_most_loaded ha ritornano None vuol dire che nessun nodo era attivo
    if nodo_most_loaded is None:
        print("Manager> Nessun nodo attivo su cui fermare il servizio")
        return

    #trova l'id del PRIMO container nel nodo di quel servizio, in base al nome del container (composto dal nome dal nome_servizio + uuid)
    id_container = next(
        (c["id"] for c in lista_nodi_stats[nodo_most_loaded] if c["nome"].startswith(servizio.servizio_name)),
        None
    )

    #se non esiste un container di quel servizio sul nodo, allora non mandare lo stop_container
    if id_container is None:
        print(f"Manager> Nessun task del servizio '{servizio.servizio_name}' trovato su {nodo_most_loaded}")
        return

    #spegne il servizio su quel nodo
    stop_container(lista_nodi[nodo_most_loaded], id_container)

#usata per inviare una richiesta al manager
def invia_richiesta(coda, azione, target):
    #mette un oggetto nella coda in modo atomico grazie ad un lock interno, questo evita le race condition
    coda.put({"azione": azione, "target": target})
    #print(f"Richiesta '{servizio.get_name()}' aggiunta alla coda")

#ciclo che il nodo manager ripete per eseguire le richieste che gli vengono mandate dall'utente
def manager(lista_nodi, coda):
    while True:
        try:
            #prende dalla coda una richiesta, se non c'è nessuna richiesta va in queue.empty -> pass
            #aspetta fino a 1 secondo per una nuova richiesta e ne gestisce una per volta, poi ricontrolla
            richiesta = coda.get(timeout=1)
            #da qui parte ad elaborare la richiesta
            try:
                print(f"\nManager> Schedulo ", richiesta["azione"], ' ', end="")
                if isinstance(richiesta["target"], Config):
                    print(" ==> ", end='')
                    richiesta["target"].stampa_config()
                #l'azione può essere: deploy, scale_down, drain_nodo (che lo disattiva nel farlo), attiva_nodo
                azione = richiesta["azione"]
                #il target può essere un servizio o un nodo
                target = richiesta["target"]

                match azione:
                    case "deploy":
                        #schedula il servizio sul nodo least loaded
                        schedula_servizio(target, lista_nodi, list_nodes(lista_nodi))
                    case "scale_down":
                        #spegne un servizio sul nodo most loaded
                        spegni_servizio(target, lista_nodi, list_nodes(lista_nodi))
                    case "drain_nodo":
                        disattiva_svuota_nodo(target, lista_nodi, coda)
                    case "attiva_nodo":
                        attiva_nodo(target, lista_nodi)
                    case _:
                        print(f"Manager> Azione sconosciuta: {azione}")
                list_nodes(lista_nodi, stampa=True)
            except Exception as e:
                print(f"Manager> Errore nella gestione della richiesta: {e}")
            finally:
                #segnala che questa richiesta è stata gestita, così il join() "rientra"
                coda.task_done()
        #se la coda è vuota, fai altro (questo forse lo modificherò in seguito, magari in un altro thread)
        except queue.Empty:
            rimuovi_container_spenti_tutti_nodi(lista_nodi)
            pass  #nessuna richiesta in coda,continua il ciclo

        #aspetta un secondo per fare una richiesta
        time.sleep(1)