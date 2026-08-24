from config import Config
from nodi import deploy_container, stop_container, remove_container
from datetime import datetime, timezone, timedelta

#crea una Config personalizzata dall'utente
def scegli_config():
    #SOLO TEST, così non runno immagini che non voglio scaricare
    immagine = input("Che immagine vuoi usare? Scrivi il nome dell'immagine esistente di cui fare il pull\n")

    servizio_name = input("Che nome vuoi dare a questo servizio custom? (Non usare nomi con il trattino '-'\n")

    comando = input("Che comando vuoi usare sul container? Lascia vuoto per nessun comando\n")
    return Config(immagine, servizio_name, command=comando)

#solo di testing, poi verrà rimossa
def scelta_deploy_container(nodo):
    config = scegli_config()
    deploy_container(nodo, config)

#questa funzione si può refactorare con una nuova funzione "scelta_container_in_nodo" e lasciare solo l'ultima linea
def scelta_stop_container(lista_nodi, lista_nodi_containers):
    print("---Nodi---")
    for nome_nodo, containers in lista_nodi_containers.items():
        print("\nNodo:", nome_nodo)
        for i, container in enumerate(containers):
            print(f"{i}) {container['nome']} {container['immagine']}")

    #chiedo all'utente di quale nodo vuole fermare il container
    nome_nodo = input("Di quale nodo vuoi FERMARE un container? (Inserisci il nome del nodo)\n")
    if nome_nodo == "nodo1" or nome_nodo == "nodo2" or nome_nodo == "nodo3":
        #se il nodo non è nella lista dei nodi con dei container vuol dire che nella funzione in cui sono stati inseriti quel nodo era già spento
        if nome_nodo not in lista_nodi_containers:
            print("Inserisci il nome di un nodo acceso")
            exit()
    else:
        print("Inserisci il nome di un nodo valido")
        exit()
    n_container = int(input("Quale container vuoi fermare?\n"))
    stop_container(lista_nodi[nome_nodo], lista_nodi_containers[nome_nodo][n_container]["id"])

#questa funzione si può refactorare con una nuova funzione "scelta_container_in_nodo" e lasciare solo l'ultima linea
def scelta_remove_container(lista_nodi, lista_nodi_containers):
    print("---Nodi---")
    for nome_nodo, containers in lista_nodi_containers.items():
        print("\nNodo:", nome_nodo)
        for i, container in enumerate(containers):
            print(f"{i}) {container['nome']} {container['immagine']} {container['status']}")

    #chiedo all'utente di quale nodo vuole rimuovere il container
    nome_nodo = input("Di quale nodo vuoi RIMUOVERE un container? (Inserisci il nome del nodo)\n")
    if nome_nodo == "nodo1" or nome_nodo == "nodo2" or nome_nodo == "nodo3":
        #se il nodo non è nella lista dei nodi con dei container vuol dire che nella funzione in cui sono stati inseriti quel nodo era già spento
        if nome_nodo not in lista_nodi_containers:
            print("Inserisci il nome di un nodo acceso")
            exit()
    else:
        print("Inserisci il nome di un nodo valido")
        exit()
    n_container = int(input("Quale container vuoi rimuovere? (Solo container con status 'down')\n"))
    remove_container(lista_nodi[nome_nodo], lista_nodi_containers[nome_nodo][n_container]["id"])

#controlla se il container è più vecchio di "soglia_minuti" minuti
#lo uso per capire se posso cancellare un container in stato di "Created" che non sta eseguendo nulla perché non si è avviato
def is_container_vecchio(container, soglia_minuti=1):
    creato = datetime.fromisoformat(container.attrs["Created"].replace("Z", "+00:00"))
    eta = datetime.now(timezone.utc) - creato
    return eta > timedelta(minutes=soglia_minuti)