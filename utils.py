from nodi import deploy_container, stop_container, remove_container
from datetime import datetime, timezone, timedelta

#SPOSTATO NELLA CLASSE Config
def crea_config(image, command, name=None):
    config= {
        "image": image,
        "command": command,
        "detach": True, #Sempre True, i container devono runnare in background
    }

    if name is not None:
        config["name"] = name

    return config

#da SPOSTARE NELLA CLASSE Config
def scegli_config():
    #SOLO TEST, così non runno immagini che non voglio scaricare
    immagine = input("Che immagine vuoi usare? \n1) hello-world, \n2) alpine\n")
    if immagine == "1":
        immagine = "hello-world"
    elif immagine == "2":
        immagine = "alpine"
    else:
        print("Inserisci un numero di immagine valido.")
        return 0

    comando = input("Che comando vuoi usare sul container? Lascia vuoto per nessun comando\n")
    return crea_config(immagine, comando)

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
            print(f"{i})" + f"{container["nome"]}" + f"{container["immagine"]}")

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
            print(f"{i})" + f"{container["nome"]}" + f"{container["immagine"]}" + f"{container["status"]}")

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

#mostra i config di un servizio in modo ordinato (capire se implementare o no)
def mostra_config(servizio):

    pass