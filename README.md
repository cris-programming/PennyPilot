# Gestore Finanze Personale

Un'applicazione web completa costruita con Python e Flask per la gestione delle finanze personali. Questo strumento permette di tracciare entrate e uscite, gestire budget mensili, analizzare le spese nel tempo e molto altro.

## ✨ Caratteristiche Principali

- **Dashboard Intuitiva:** Grafici e riquadri riassuntivi per una visione d'insieme immediata dello stato finanziario.
- **Gestione Transazioni:** Aggiunta, modifica ed eliminazione di entrate e uscite.
- **Transazioni Ricorrenti:** Impostazione di movimenti automatici (stipendi, abbonamenti) con frequenza personalizzabile.
- **Categorizzazione e Budget:** Assegnazione di categorie alle spese e impostazione di budget mensili con barre di progresso visive.
- **Analisi Storica:** Pagina dedicata con grafici interattivi per analizzare l'andamento del patrimonio, il flusso di cassa e le spese per categoria nel tempo.
- **Reportistica Avanzata:** Esportazione dei dati annuali e mensili in formato CSV e PDF.
- **Interfaccia Moderna:** UI responsiva con sidebar verticale.

## 🛠️ Stack Tecnologico

- **Backend:** Python, Flask, SQLAlchemy, Flask-Migrate
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Grafici:** Chart.js
- **Generazione PDF:** WeasyPrint

## 🚀 Installazione e Avvio

Per avviare il progetto in locale, segui questi passaggi:

1.  **Clona il repository:**
    ```bash
    git clone [https://github.com/TUO_USERNAME/NOME_REPO.git](https://github.com/TUO_USERNAME/NOME_REPO.git)
    cd NOME_REPO
    ```

2.  **Crea e attiva un ambiente virtuale:**
    ```bash
    # Su Windows
    python -m venv venv
    venv\Scripts\activate

    # Su macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Installa le dipendenze:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Inizializza il database:**
    ```bash
    # Assicurati che esista il file .flaskenv con
    FLASK_APP=app
    # poi esegui
    flask db upgrade
    ```

5.  **Avvia l'applicazione:**
    ```bash
    python run.py
    ```
L'applicazione sarà accessibile all'indirizzo `http://127.0.0.1:5000`.