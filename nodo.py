import docker
from docker.errors import DockerException

#questa classe tiene traccia delle informazioni del singolo nodo
class Nodo:
    def __init__(self, nome, ip, timeout=3):
        self.nome = nome
        self.ip = ip
        self.timeout = timeout
        #crea un oggetto DockerClient che uso per comunicare con quel container DinD
        try:
            #il timeout è il tempo per cui deve provare a connettersi prima di smettere in caso in cui il nodo sia down
            self.client = docker.DockerClient(base_url=f'tcp://{ip}:2375', timeout=self.timeout)
        except DockerException:
            print(f"Attenzione: impossibile connettersi a {nome} ({ip}) alla creazione. Verrà considerato down finché non risponde.")
            self.client = None
        #serve tenerne traccia per rilanciare i container del nodo in un altro nodo in caso di crash
        self.container_attivi = {}
        #il nodo inizia da disponibile, nel caso in cui si voglia svuotare il nodo e non usarlo (per manutenzione)
        #questa variabile verrà impostata a False
        self.disponibile = True

    #controlla se il nodo è attivo o spento, nel caso in cui sia spento prova a riconnettersi
    def is_up(self):
        #se il nodo non è connesso, allora prova a connettersi
        if self.client is None:
            try:
                self.client = docker.DockerClient(base_url=f'tcp://{self.ip}:2375', timeout=self.timeout)
            except DockerException:
                return False
        #se il nodo è connesso, fa il ping per vedere se continua a essere connesso, se non lo è ritorna False
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def is_disponibile(self):
        return self.disponibile

    #In questo file metto le funzioni che rigurdano la gestione dei container all'interno dei nodi, include le operazioni
    #eseguite all'interno di un nodo dal nodo worker

    #ritorna info solo dei container attivi su questo nodo
    def info_container_attivi(self):
        try:
            info_totali = []
            for container in self.client.containers.list():
                comando = container.attrs["Config"]["Cmd"]
                info_totali.append({
                    "nome": container.name,
                    "id": container.short_id,
                    "immagine": container.image.tags[0] if container.image.tags else "nessun tag",
                    "comando": " ".join(comando) if comando else None
                })
            self.container_attivi = info_totali
            return info_totali
        except Exception:
            return self.container_attivi

    #ritorna info di tutti i container, sia spenti che attivi, su questo nodo
    def info_container_spenti_e_attivi(self):
        info_totali = []
        for container in self.client.containers.list(all=True):
            info_totali.append({
                "nome": container.name,
                "id": container.short_id,
                "immagine": container.image.tags[0] if container.image.tags else "nessun tag",
                "status": container.status
            })
        return info_totali