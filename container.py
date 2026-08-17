#In questo file metto le funzioni che rigurdano la gestione dei container all'interno dei nodi, include le operazioni
#eseguite all'interno di un nodo dal nodo worker

#ritorna info solo dei container attivi su questo nodo
def info_container_attivi(client):
    info_totali = []
    for container in client.containers.list():
        info_totali.append({
            "nome": container.name,
            "id": container.short_id,
            "immagine": container.image.tags[0] if container.image.tags else "nessun tag",
        })
    return info_totali

#ritorna info di tutti i container, sia spenti che attivi, su questo nodo
def info_container_spenti_e_attivi(client):
    info_totali = []
    for container in client.containers.list(all=True):
        info_totali.append({
            "nome": container.name,
            "id": container.short_id,
            "immagine": container.image.tags[0] if container.image.tags else "nessun tag",
            "status": container.status
        })
    return info_totali