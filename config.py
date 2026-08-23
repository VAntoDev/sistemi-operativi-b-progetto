class Config:
    def __init__(self, image, command=None, name=None):
        self.image = image
        self.command = command
        self.name = name

    def get_name(self):
        return self.name

    def stampa_config(self):
        print("Immagine: " + f'{self.image}' + f'{" | Comando: " + self.command if self.command is not None else ""}' + f'{" | Nome: " + self.name if self.name is not None else ""}')
        pass

#DEVI FINIRE CONFIG E POI FINIRE LA FUNZIONE "CREA 1 SERVIZIO CHE C'È NEL MENU SERVIZI.
#DEVI FINIRE CONFIG E POI FINIRE LA FUNZIONE "CREA 1 SERVIZIO CHE C'È NEL MENU SERVIZI.
#DEVI FINIRE CONFIG E POI FINIRE LA FUNZIONE "CREA 1 SERVIZIO CHE C'È NEL MENU SERVIZI.
#DEVI FINIRE CONFIG E POI FINIRE LA FUNZIONE "CREA 1 SERVIZIO CHE C'È NEL MENU SERVIZI.
#DEVI FINIRE CONFIG E POI FINIRE LA FUNZIONE "CREA 1 SERVIZIO CHE C'È NEL MENU SERVIZI.
#DEVI FINIRE CONFIG E POI FINIRE LA FUNZIONE "CREA 1 SERVIZIO CHE C'È NEL MENU SERVIZI.
#poi fare tutto il resto...