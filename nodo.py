import docker

#questa classe tiene traccia delle informazioni del singolo nodo
class Nodo:
    def __init__(self, nome, ip, timeout=3):
        self.nome = nome
        self.ip = ip
        #crea un oggetto DockerClient che uso per comunicare con quel container DinD
        #il timeout è il tempo per cui deve provare a connettersi prima di smettere in caso in cui il nodo sia down
        self.client = docker.DockerClient(base_url=f'tcp://{ip}:2375', timeout=timeout)

    #controlla se il nodo è attivo o spento
    def is_up(self):
        try:
            #fa un ping a quel nodo, se risponde vuol dire che è ancora acceso
            self.client.ping()
            return True
        except Exception:
            return False

    #In questo file metto le funzioni che rigurdano la gestione dei container all'interno dei nodi, include le operazioni
    #eseguite all'interno di un nodo dal nodo worker

    #ritorna info solo dei container attivi su questo nodo
    def info_container_attivi(self):
        info_totali = []
        for container in self.client.containers.list():
            info_totali.append({
                "nome": container.name,
                "id": container.short_id,
                "immagine": container.image.tags[0] if container.image.tags else "nessun tag",
            })
        return info_totali

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