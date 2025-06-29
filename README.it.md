[Read this README in English](README.md)

---

# Gestore Finanze Personale

Un'applicazione web completa costruita con Python e Flask per la gestione delle finanze personali. Questo strumento permette di tracciare entrate e uscite, gestire budget mensili, analizzare le spese nel tempo e molto altro.

## ✨ Caratteristiche Principali

- **Dashboard Intuitiva:** Grafici e riquadri riassuntivi per una visione d'insieme immediata dello stato finanziario.
- **Gestione Transazioni:** CRUD (Create, Read, Update, Delete) completo per entrate e uscite.
- **Transazioni Ricorrenti:** Impostazione di movimenti automatici (stipendi, abbonamenti) con frequenza personalizzabile.
- **Categorizzazione e Budget:** Assegnazione di categorie alle spese e impostazione di budget mensili con barre di progresso visive e insight comparativi (es. vs. mese precedente).
- **Analisi Storica:** Pagina dedicata con grafici interattivi per analizzare l'andamento del patrimonio, il flusso di cassa e le spese per categoria nel tempo.
- **Reportistica Avanzata:** Esportazione dei dati annuali e mensili in formato CSV e PDF.
- **Interfaccia Moderna:** UI responsiva con sidebar verticale a icone.

## 🛠️ Stack Tecnologico

- **Backend:** Python, Flask, SQLAlchemy, Flask-Migrate
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Grafici:** Chart.js
- **Generazione PDF:** WeasyPrint
- **Icone:** Font Awesome

## 🚀 Installazione e Avvio

Per avviare il progetto in locale, segui questi passaggi:

1.  **Clona il repository:**
    ```bash
    git clone [https://github.com/cris-programming/PennyPilot.git](https://github.com/cris-programming/PennyPilot.git)
    cd PennyPilot
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
    *Assicurati che esista il file `.flaskenv` nella cartella principale con `FLASK_APP=app`.*
    ```bash
    flask db upgrade
    ```

5.  **Avvia l'applicazione:**
    ```bash
    python run.py
    ```
L'applicazione sarà accessibile all'indirizzo `http://127.0.0.1:5000`.