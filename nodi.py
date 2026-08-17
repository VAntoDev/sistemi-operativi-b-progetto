#In questo file metto tutte le funzioni che riguardano la gestione dei nodi, include le operazioni eseguite all'esterno
#di un nodo dal nodo manager

import docker
from container import info_container_attivi, info_container_spenti_e_attivi
from docker.errors import DockerException
#usato per le animazioni di caricamento (altrimenti non capisco se si è bloccato tutto)
from yaspin import yaspin

#crea un DockerClient per connettersi a quel nodo (che deve essere già acceso), per mandare comandi a esso
def crea_client(ip, timeout=3):
    try:
        return docker.DockerClient(base_url=f'tcp://{ip}:2375', timeout=timeout)
    #se il tempo di "timeout" passa e non sono riuscito a connettermi, allora ritorna 0 per indicare che il nodo è down
    except (DockerException, Exception) as e:
        return 0

# mostra le informazioni relative ai nodi connessi in questo momento
# nodi è un dizionario contenente tutti nodi di cui si vuole elencare lo stato
def check_node_status(client):
    #fa un ping al nodo, se risponde vuol dire che è attivo e ritorna "up"
    try:
        client.ping()
        return "UP"
    #fa un ping al nodo, se non risponde vuol dire che è spento e ritorna "down"
    except Exception:
        return "DOWN"

#stampa lo stato attuale di tutti i nodi, con anche i loro container attivi
def list_nodes(nodi, tutti=False):
    # lista dei container attivi per ogni nodo
    diz_nodo_containers = {}
    for nome, client in nodi.items():
        #controlla se il nodo è attivo o spento
        stato = check_node_status(client)

        if stato == "UP":
            if tutti == False:
                info_containers = info_container_attivi(client)
                print(f"{nome} | {stato} | Container attivi: {info_containers}")
                #aggiunge le informazioni alla lista dei containers attivi di ogni nodo
                diz_nodo_containers[nome] = info_containers
            else:
                info_containers = info_container_spenti_e_attivi(client)
                print(f"{nome} | {stato} | Container attivi: {info_containers}")
                # aggiunge le informazioni alla lista dei containers attivi di ogni nodo
                diz_nodo_containers[nome] = info_containers
        else:
            print(f"{nome} | {stato}")
    return diz_nodo_containers

#fa partire un container sul nodo specificato, con l'immagine e il comando del dizionario "config"
def deploy_container(node, config):
    try:
        node.containers.run(**config)
    except (DockerException, Exception) as e:
        print("Errore nel deploy del container: ", e)
    pass

#ferma un container dato il suo nodo e il suo id
def stop_container(node, id_container):
    try:
        with yaspin(text="Fermo il container..."):
            node.containers.get(id_container).stop() #stop attende che il processo termini, per questo può volerci un po' per chiudere il container
        print("Container fermato.\n")
    except (DockerException, Exception) as e:
        print("Errore nello stop del container: ", e)

#rimuove un container dato il suo nodo e il suo id
def remove_container(node, id_container):
    try:
        with yaspin(text="Rimuovo il container..."):
            node.containers.get(id_container).remove() #ricorda, per rimuovere il container deve prima essere spento
        print("Container rimosso.\n")
    except (DockerException, Exception) as e:
        print("Errore nella rimozione del container, controlla che fosse spento. Errore: ", e)