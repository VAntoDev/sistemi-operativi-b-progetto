import time
from manager import invia_richiesta
from nodi import list_nodes
from nodo import Nodo


class Menu:
    def __init__(self, lista_nodi, coda, servizi_validi):
        self.lista_nodi = lista_nodi
        self.coda = coda
        self.servizi = servizi_validi

    def avvia_menu(self):
        print("\n---A.V.O. è attivo---")
        while True:
            #scelta del menu
            scelta = input(f"\n---Menu Principale---\nScegli il numero di una voce dal menu:\n"
                            f"1) Menu - Servizi\n"
                            f"2) Menu - Stato Nodi\n"
                            f"3) Aggiungi Configurazione Servizio\n"
                            f"4) Uscita\n"
                            f"5) Uscita Forzata (senza finire di avviare i container in coda)\n")
            match scelta:
                #menu servizi
                case "1":
                    self.menu_servizi()
                #menu stato nodi
                case "2":
                    self.menu_stato_nodi()
                #menu amministratore
                case "3":
                    self.aggiungi_config_servizio()
                #exit normale, attende che la coda abbia terminato di eseguire il container prima di chiudersi
                case "4":
                    self.coda.join()
                    break
                #exit forzata, chiude tutto senza aspettare che il thread manager abbia finito con la coda.
                case "5":
                    break
                case _:
                    print("Opzione non valida, metti un numero tra quelli nel menù.")
            time.sleep(3)

    def menu_servizi(self):
        while True:
            comando = input(f"\n---Menu Servizi---\nScegli una voce dal menù:\n"
                            f"1) Crea replica di 1 servizio\n"
                            f"2) Scala N repliche di un servizio (da implementare)\n"
                            f"3) Rimuovi replica di 1 servizio (da implementare)\n"
                            f"4) Rimuove tutte le repliche di 1 servizio (da implementare)\n"
                            f"5) Mostra status di 1 servizio sui nodi (da implementare)\n"
                            f"6) Torna al Menu Principale\n")
            match comando:
                case "1":
                    # crea 1 replica di un servizio
                    print("Scegli quale servizio avviare tra quelli disponibili:")
                    # stampa i servizi disponibili
                    for i, servizio in enumerate(self.servizi, start=1):
                        print(f"{i}) ", end="")
                        servizio.stampa_config()
                    # prende in input il servizio dell'utente
                    num_servizio = input("")
                    servizio = self.servizi[int(num_servizio) - 1]
                    # manda la richiesta al thread Manager così che lo scheduli sul nodo least loaded
                    invia_richiesta(self.coda, servizio)

                case "2":
                    pass

                case "3":
                    pass

                case "4":
                    pass

                case "5":
                    pass

                #torna al menu principale
                case "6":
                    break

                case _:
                    print("Opzione non valida, riprova.")
            #stampa di nuovo il menu solo se la task della coda è stata soddisfatta (in Manager)
            self.coda.join()
            time.sleep(1)

    def menu_stato_nodi(self):
        while True:
            comando = input(f"\n---Menu Servizi---\nScegli una voce dal menù:\n"
                            f"1) Stampa stato e servizi attivi sui nodi\n"
                            f"2) Stampa stato e TUTTI i servizi sui nodi\n"
                            f"3) Svuota un nodo (da implementare)\n"
                            f"4) Torna al Menu Principale\n")
            match comando:
                case "1":
                    #stampa stato dei nodi e i loro servizi attivi
                    list_nodes(self.lista_nodi, stampa=True)
                case "2":
                    #stampa stato dei nodi e i servizi sia attivi che spenti
                    list_nodes(self.lista_nodi, stampa=True, tutti=True)
                case "3":
                    pass

                case "4":
                    break

                case _:
                    print("Opzione non valida, riprova.")
            time.sleep(1)

    def aggiungi_config_servizio(self):
        pass

def VECCHIO_avvia_menu(lista_nodi, coda, servizi_validi):
    # menu per l'utente così può specificare che servizio vuole fare runnare
    while True:
        comando = input(f"---\nManda un servizio da schedulare ('exit' per uscire, 'stampa' per stampare i nodi con container attuali): \nServizi disponibili: {servizi_validi}\n")
        # uscita forzata dal programma, senza aspettare che il manager abbia finito con la coda.
        if comando == "exit forzata":
            break
        # uscita "soft" dal programma, aspetta che il manager finisca le richieste in coda prima di chiudersi
        if comando == "exit":
            # blocca l'esecuzione finché il manager non ha finito tutto quello che c'era in coda (tracciato da task_done)
            coda.join()
            break
        if comando == "stampa":
            list_nodes(lista_nodi, stampa=True)
            continue
        if comando == "stampa_spenti":
            list_nodes(lista_nodi, tutti=True, stampa=True)
        if comando not in servizi_validi:
            print("Comando o servizio non disponibile, riprova con uno dei comandi/servizi specificati sopra.")
            continue
        # invia la richiesta all'oggetto "coda", condiviso con il thread manager
        invia_richiesta(coda, comando)
        # per printare di nuovo la richiesta di input dopo l'operazione aspetta 3 secondi (posso sostituirlo dopo con un .join() )
        time.sleep(3)