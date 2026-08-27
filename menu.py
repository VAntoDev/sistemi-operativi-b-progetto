#questa classe gestisce il Menu mostrato all'utente
import time
from manager import invia_richiesta
from cluster import list_nodes, disponibilita_nodi
from nodo import Nodo
from utils import scegli_config


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
                            f"5) Uscita Forzata (senza finire di gestire le richieste in coda)\n")
            match scelta:
                #menu servizi
                case "1":
                    self.menu_servizi()
                #menu stato nodi
                case "2":
                    self.menu_stato_nodi()
                #per aggiungere un nuovo servizio specificando immagine e comando:
                #(ho scelto alpine e hello-world come config di default, le altre aggiunte dall'utente vanno pullate per ogni nodo)
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
            time.sleep(1)

    def menu_servizi(self):
        while True:
            comando = input(f"\n---Menu Servizi---\nScegli una voce dal menù:\n"
                            f"1) Crea replica di 1 servizio\n"
                            f"2) Scala N repliche di un servizio\n"
                            f"3) Torna al Menu Principale\n")
            match comando:
                case "1":
                    # crea 1 replica di un servizio
                    print("Scegli quale servizio avviare tra quelli disponibili:")
                    # stampa i servizi disponibili
                    self.stampa_servizi()
                    # prende in input il servizio dell'utente
                    num_servizio = input("")

                    try:
                        servizio = self.servizi[int(num_servizio) - 1]
                        # manda la richiesta al thread Manager così che lo scheduli sul nodo least loaded
                        invia_richiesta(self.coda, "deploy", servizio)
                    except ValueError:
                        print("Errore, inserisci un numero valido")
                        continue
                    except IndexError:
                        print("Errore, numero di servizio non in lista")
                        continue

                case "2":
                    #alza, abbassa o azzera il numero di repliche di un servizio
                    print("Scegli quale servizio vuoi scalare")
                    self.stampa_servizi()
                    #prende in input il servizio dell'utente
                    try:
                        num_servizio = input("")
                        servizio = self.servizi[int(num_servizio) - 1]
                        num_repliche = input("Scegli il numero di repliche che vuoi avere per il servizio scelto\n")

                        num_repliche = int(num_repliche)
                        if num_repliche < 0:
                            print("Il numero di repliche non può essere negativo")
                            continue

                        self.scala_repliche(num_repliche, servizio)
                    except ValueError:
                        print("Errore, inserisci un numero valido")
                        continue
                    except IndexError:
                        print("Errore, numero di servizio non in lista")
                        continue

                #torna al menu principale
                case "3":
                    break

                case _:
                    print("Opzione non valida, riprova.")
            #stampa di nuovo il menu solo se la task della coda è stata soddisfatta (in Manager)
            self.coda.join()
            time.sleep(1)

    def menu_stato_nodi(self):
        while True:
            comando = input(f"\n---Menu Stato Nodi---\nScegli una voce dal menù:\n"
                            f"1) Stampa stato e task attivi sui nodi\n"
                            f"2) Stampa stato e task attivi e spenti sui nodi\n"
                            f"3) Svuota un nodo \n"
                            f"4) Attiva un nodo se è in DRAIN \n"
                            f"5) Torna al Menu Principale\n")
            match comando:
                case "1":
                    #stampa stato dei nodi e i loro servizi attivi
                    list_nodes(self.lista_nodi, stampa=True)
                    nodi_non_attivi = disponibilita_nodi(self.lista_nodi, attivi=False)
                    if nodi_non_attivi:
                        print("Nodi in stato di DRAIN:", " ".join(nodi_non_attivi))
                case "2":
                    #stampa stato dei nodi e i servizi sia attivi che spenti
                    list_nodes(self.lista_nodi, stampa=True, tutti=True)
                    nodi_non_attivi = disponibilita_nodi(self.lista_nodi, attivi=False)
                    if nodi_non_attivi:
                        print("Nodi in stato di DRAIN:", " ".join(nodi_non_attivi))
                case "3":
                    #fa scegliere all'utente fra i nodi attivi uno da mettere in DRAIN, i suoi container verranno spostati sugli altri nodi
                    nodi_attivi = disponibilita_nodi(self.lista_nodi)

                    if not nodi_attivi:
                        print("Nessun nodo disponibile per il drain.")
                        continue
                    try:
                        print("Scegli quale nodo vuoi svuotare (andrà in stato di DRAIN)")
                        for i, nome in enumerate(nodi_attivi, start=1):
                            print(f"{i}) {nome}")

                        num_nodo = input("")
                        nome_nodo_scelto = nodi_attivi[int(num_nodo) - 1]

                        invia_richiesta(self.coda, "drain_nodo", nome_nodo_scelto)
                    except ValueError:
                        print("Errore, inserisci un numero valido")
                    except IndexError:
                        print("Errore, numero di nodo non in lista")
                case "4":
                    #fa scegliere all'utente fra i nodi in DRAIN da riattivare, da qui potrà riprendere richieste di deploy
                    nodi_non_attivi = disponibilita_nodi(self.lista_nodi, attivi=False)

                    if not nodi_non_attivi:
                        print("Nessun nodo è in stato di DRAIN.")
                        continue

                    print("Scegli quale nodo vuoi attivare (sarà di nuovo considerato per il deploy)")
                    for i, nome in enumerate(nodi_non_attivi, start=1):
                        print(f"{i}) {nome}")
                    try:
                        num_nodo = input("")
                        nome_nodo_scelto = nodi_non_attivi[int(num_nodo) - 1]

                        invia_richiesta(self.coda, "attiva_nodo", nome_nodo_scelto)
                    except ValueError:
                        print("Errore, inserisci un numero valido")
                    except IndexError:
                        print("Errore, numero di nodo non in lista")
                case "5":
                    break

                case _:
                    print("Opzione non valida, riprova.")
            time.sleep(1)

    def aggiungi_config_servizio(self):
        #faccio scegliere all'utente una nuova configurazione, ovvero immagine comando e nome del servizio
        nuova_config = scegli_config()

        #se la configurazione era valida, allora la aggiunge alla lista
        if nuova_config is not None:
            self.servizi.append(nuova_config)

    def stampa_servizi(self):
        for i, servizio in enumerate(self.servizi, start=1):
            print(f"{i}) ", end="")
            servizio.stampa_config()

    #conta quanti container di un certo servizio sono attivi su TUTTI i nodi, ritorna quel totale
    def conta_repliche(self, servizio):
        lista_nodi_stats = list_nodes(self.lista_nodi)
        totale = 0
        for nome_nodo, containers in lista_nodi_stats.items():
            for c in containers:
                #riconosce i servizi in base al nome che gli è stato dato al deploy
                if c["nome"].startswith(servizio.servizio_name):
                    totale += 1
        return totale

    def scala_repliche(self, num_repliche, servizio):
        #ottengo info sul numero di repliche di quel servizio attualmente
        repliche_attuali = self.conta_repliche(servizio)
        #controllo la differenza fra quelle che vuole l'utente e quelle attuali
        differenza = num_repliche - repliche_attuali

        #se la differenza è un numero positivo, allora l'utente vuole aumentare il numero di repliche quindi deploy
        if differenza > 0:
            #servono più repliche quindi manda "differenza" richieste di deploy
            for _ in range(differenza):
                invia_richiesta(self.coda, "deploy", servizio)
            print(f"Richieste {differenza} nuove repliche di '{servizio.servizio_name}'")

        elif differenza < 0:
            #ci sono troppe repliche quindi manda "abs(differenza)" richieste di scale_down
            for _ in range(-differenza):
                invia_richiesta(self.coda, "scale_down", servizio)
            print(f"Richieste {-differenza} rimozioni di repliche di '{servizio.servizio_name}'")

        else:
            print(f"'{servizio.servizio_name}' ha già {num_repliche} repliche attive.")
