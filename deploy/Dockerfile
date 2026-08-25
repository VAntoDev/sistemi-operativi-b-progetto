FROM python:3.12-slim

WORKDIR /app

#copia solo requirements.txt prima, così Docker riusa la cache se il codice
#cambia ma le dipendenze no (build più veloci nelle iterazioni successive)
COPY deploy/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

#copia il codice dell'orchestratore
COPY . .

#avvia l'orchestraore
CMD ["python", "main.py"]