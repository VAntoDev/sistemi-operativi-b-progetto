#usata per definre i servizi che possono essere eseguiti dall'orchestratore
class Config:
    def __init__(self, image, servizio_name, command=None, name=None):
        self.image = image
        self.command = command
        #nome personalizzato del container
        self.name = name
        #nome di questo specifico servizio definito dall'utente
        self.servizio_name = servizio_name

    def get_name(self):
        return self.name

    def stampa_config(self):
        print("Immagine: " + f'{self.image}' +
              f'{" | Nome Servizio: " + self.servizio_name if self.servizio_name is not None else ""}'
              f'{" | Comando: " + self.command if self.command is not None else ""}' +
              f'{" | Nome Container: " + self.name if self.name is not None else ""}')
        pass