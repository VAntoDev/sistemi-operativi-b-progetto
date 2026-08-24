from config import Config
from datetime import datetime, timezone, timedelta

#crea una Config personalizzata dall'utente,
def scegli_config():
    immagine = input("Che immagine vuoi usare? Scrivi il nome dell'immagine esistente di cui fare il pull\n")

    servizio_name = input("Che nome vuoi dare a questo servizio custom? (Non usare nomi con il trattino '-'\n")

    #se l'utente ha inserito un nome con "-" non faccio usare la configurazione
    if "-" in servizio_name:
        print("Info> Errore: il nome del servizio non può contenere '-'.")
        return None

    comando = input("Che comando vuoi usare sul container? Lascia vuoto per nessun comando\n")
    return Config(immagine, servizio_name, command=comando)

#controlla se il container è più vecchio di "soglia_minuti" minuti
#lo uso per capire se posso cancellare un container in stato di "Created" che non sta eseguendo nulla perché non si è avviato
def is_container_vecchio(container, soglia_minuti=1):
    creato = datetime.fromisoformat(container.attrs["Created"].replace("Z", "+00:00"))
    eta = datetime.now(timezone.utc) - creato
    return eta > timedelta(minutes=soglia_minuti)