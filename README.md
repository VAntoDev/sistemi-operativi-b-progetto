# A.V. Orchestrator

Semplice orchestratore scritto in Python e usando l'API di Docker. L'orchestratore ha bisogno di una rete di nodi per
funzionare, tali nodi sono implementati tramite container DinD e l'orchestratore stesso viene eseguito su un ulteriore
nodo della rete.

## Requisiti
Per eseguire l'orchestratore è necessario installare:
- Docker (con Docker Compose)
- Un sistema in grado di eseguire container con privileged: true (per il funzionamento dei container DinD)

Durante il primo build dell'orchestratore è necessario avere una connessione a internet per poter scaricare le immagini Docker 
e le dipendenze richieste.

## Cosa viene creato all'avvio e durante l'uso dell'orchestratore
All'avvio del progetto verranno creati o utilizzati se già presenti i seguenti componenti Docker:
- 3 container che rappresentano i nodi worker (immagine DinD. Nomi: nodo1avo, nodo2avo, nodo3avo) 
- 1 container che rappresenta il nodo manager (immagine Python modificata con Dockerfile, Nome: nodo-manager-avo)
- 1 rete docker (nome: rete-cluster-avo)
- 4 immagini docker (immagine del Dockerfile, immagine docker:dind, immagine alpine:latest, immagine hello-world:latest)

## Avviare il progetto
1) Clonare il repository e spostarsi nella directory deploy del progetto:
```bash
cd repo_progetto/deploy
```
2) Avviare i nodi worker:
```bash
docker compose up -d nodo1avo nodo2avo nodo3avo
```
3) Avviare l'orchestratore:
```bash
docker compose run --rm nodo-manager-avo
```
L'orchestratore verrà avviato in modalità interattiva e sarà possibile utilizzare il menu tramite il suo terminale.
## Fermare il progetto
Per fermare tutti i nodi:
```bash
docker compose down
```

## Simulare la caduta di un nodo
Oltre alle funzionalità offerte dal menù dell'orchestratore, è possibile vedere come reagisce il sistema alla caduta di un nodo worker.
```bash
docker kill nodo1avo
```
Non è consigliato usare ```docker stop``` in quanto i container DinD terminano i loro container prima di arrestarsi, 
non permettendo di far notare all'orchestratore che dei servizi si sono arrestati in modo anomalo.