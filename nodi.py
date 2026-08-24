#In questo file metto tutte le funzioni che riguardano la gestione dei nodi, include le operazioni eseguite all'esterno
#di un nodo dal nodo manager

import docker
from docker.errors import DockerException
#usato per le animazioni di caricamento (altrimenti non capisco se si è bloccato tutto)
from yaspin import yaspin

from nodo import Nodo

#stampa lo stato attuale di tutti i nodi, con anche i loro container attivi
def list_nodes(nodi, tutti=False, stampa=False):
    # lista dei container attivi per ogni nodo
    diz_nodo_containers = {}
    for nome, nodo in nodi.items():
        #controlla se il nodo è attivo o spento
        stato = nodo.is_up()

        if stato:
            if tutti == False:
                info_containers = nodo.info_container_attivi()
                if stampa == True:
                    print(f"\n{nome} | {'UP' if stato else 'DOWN'} | Servizi attivi(" + f'{len(info_containers)}' + "): ")
                    for container in info_containers:
                        for attributo, valore in container.items():
                            print(attributo, ':', valore, "| ", end="")
                        print()
                #aggiunge le informazioni alla lista dei containers attivi di ogni nodo
                diz_nodo_containers[nome] = info_containers
            else:
                info_containers = nodo.info_container_spenti_e_attivi()
                if stampa == True:
                    print(f"\n{nome} | {'UP' if stato else 'DOWN'} | Servizi spenti e attivi(" + f'{len(info_containers)}' + "): ")
                    for container in info_containers:
                        for attributo, valore in container.items():
                            print(attributo, ':', valore, "| ", end="")
                        print()
                # aggiunge le informazioni alla lista dei containers attivi di ogni nodo
                diz_nodo_containers[nome] = info_containers
        else:
            print(f"{nome} | {'UP' if stato else 'DOWN'}")
    return diz_nodo_containers

#ritorna solo i nodi disponibili per il drain, se attivi=False allora ritorna solo i nodi disattivati che possono essere attivati
def disponibilita_nodi(nodi, attivi=True):
    nomi_nodi = []
    for nome, nodo in nodi.items():
        disponibilita = nodo.is_disponibile()
        #se il nodo è allo stesso stato di "attivi" allora viene aggiunto ai nodi che verranno ritornati
        if disponibilita == attivi:
            nomi_nodi.append(nome)
    return nomi_nodi

#fa partire un container sul nodo specificato, con l'immagine e il comando del dizionario "config"
def deploy_container(node, config):
    try:
        node.client.containers.run(**config)
        print(f"Container: {config['image']} deployato (run) sul nodo: {node.nome}")
    except (DockerException, Exception) as e:
        #può dare errore se prova a startare un container con un nome già esistente sul nodo, è possibile succeda ma molto poco probabile
        print("Errore nel deploy del container: ", e)

#ferma un container dato il suo nodo e il suo id
def stop_container(node, id_container):
    try:
        with yaspin(text="Fermo il container..."):
            node.client.containers.get(id_container).stop() #stop attende che il processo termini, per questo può volerci un po' per chiudere il container
        print("Container fermato.\n")
    except (DockerException, Exception) as e:
        print("Errore nello stop del container: ", e)

#rimuove un container dato il suo nodo e il suo id
def remove_container(node, id_container):
    try:
        with yaspin(text="Rimuovo il container..."):
            node.client.containers.get(id_container).remove() #ricorda, per rimuovere il container deve prima essere spento
        print("Container rimosso.\n")
    except (DockerException, Exception) as e:
        print("Errore nella rimozione del container, controlla che fosse spento. Errore: ", e)