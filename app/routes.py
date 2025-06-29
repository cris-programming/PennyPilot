from flask import render_template, request, redirect, url_for, flash, Response
from app import app, db
from app.models import Transazione, TransazioneRicorrente, Categoria, Budget
from datetime import date, datetime
from sqlalchemy import extract, or_
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import io
import csv
from weasyprint import HTML

# --- FUNZIONI DI SUPPORTO ---
def genera_occorrenze_da_regole(start_date, end_date):
    regole = TransazioneRicorrente.query.all()
    occorrenze = []
    for regola in regole:
        data_controllo = regola.data_inizio
        if regola.frequenza == "WEEKLY":
            incremento = relativedelta(weeks=1)
        elif regola.frequenza == "MONTHLY":
            incremento = relativedelta(months=1)
        elif regola.frequenza == "QUARTERLY":
            incremento = relativedelta(months=3)
        elif regola.frequenza == "SEMIANNUALLY":
            incremento = relativedelta(months=6)
        else:
            incremento = relativedelta(years=1)
        while data_controllo <= end_date:
            if data_controllo >= start_date and (
                regola.data_fine is None or data_controllo <= regola.data_fine
            ):
                occorrenza = Transazione(
                    id=f"r{regola.id}_{data_controllo.strftime('%Y%m%d')}",
                    descrizione=f"{regola.descrizione}",
                    importo=regola.importo,
                    tipo=regola.tipo,
                    data=data_controllo,
                )
                occorrenze.append(occorrenza)
            if regola.data_inizio > data_controllo + incremento:
                break
            data_controllo += incremento
            if regola.data_fine and data_controllo > regola.data_fine:
                break
    return occorrenze

# --- ROUTE PRINCIPALI ---
@app.route("/")
def index():
    today = date.today()
    nomi_mesi = [
        "Gennaio",
        "Febbraio",
        "Marzo",
        "Aprile",
        "Maggio",
        "Giugno",
        "Luglio",
        "Agosto",
        "Settembre",
        "Ottobre",
        "Novembre",
        "Dicembre",
    ]

    # Calcoli per i riquadri e i grafici a torta
    tutte_le_transazioni_reali = Transazione.query.all()
    transazioni_passate = [t for t in tutte_le_transazioni_reali if t.data <= today]
    ricorrenti_passate = genera_occorrenze_da_regole(date(2000, 1, 1), today)
    transazioni_attuali_totali = transazioni_passate + ricorrenti_passate
    entrate_attuali_totali = sum(
        t.importo for t in transazioni_attuali_totali if t.tipo == "entrata"
    )
    uscite_attuali_totali = sum(
        t.importo for t in transazioni_attuali_totali if t.tipo == "uscita"
    )
    saldo_attuale = entrate_attuali_totali - uscite_attuali_totali

    ultimo_giorno_mese_corrente = today.replace(day=1) + relativedelta(
        months=1, days=-1
    )
    transazioni_reali_future_nel_mese = [
        t
        for t in tutte_le_transazioni_reali
        if t.data > today and t.data <= ultimo_giorno_mese_corrente
    ]
    ricorrenti_future_nel_mese = genera_occorrenze_da_regole(
        today + relativedelta(days=1), ultimo_giorno_mese_corrente
    )
    entrate_future_mese = sum(
        t.importo
        for t in (transazioni_reali_future_nel_mese + ricorrenti_future_nel_mese)
        if t.tipo == "entrata"
    )
    uscite_future_mese = sum(
        t.importo
        for t in (transazioni_reali_future_nel_mese + ricorrenti_future_nel_mese)
        if t.tipo == "uscita"
    )
    saldo_fine_mese = saldo_attuale + entrate_future_mese - uscite_future_mese

    prossimo_mese_dt_inizio = today.replace(day=1) + relativedelta(months=1)
    prossimo_mese_dt_fine = prossimo_mese_dt_inizio + relativedelta(months=1, days=-1)
    spese_reali_prossimo_mese = [
        t
        for t in tutte_le_transazioni_reali
        if t.tipo == "uscita"
        and t.data >= prossimo_mese_dt_inizio
        and t.data <= prossimo_mese_dt_fine
    ]
    spese_ricorrenti_prossimo_mese = [
        t
        for t in genera_occorrenze_da_regole(
            prossimo_mese_dt_inizio, prossimo_mese_dt_fine
        )
        if t.tipo == "uscita"
    ]
    spese_prossimo_mese_totali = sum(
        t.importo for t in (spese_reali_prossimo_mese + spese_ricorrenti_prossimo_mese)
    )
    prossimo_mese_info = {
        "nome": nomi_mesi[prossimo_mese_dt_inizio.month - 1],
        "spese": spese_prossimo_mese_totali,
    }

    primo_giorno_mese_corrente = today.replace(day=1)
    trans_reali_mese_corrente = [
        t
        for t in tutte_le_transazioni_reali
        if t.data >= primo_giorno_mese_corrente
        and t.data <= ultimo_giorno_mese_corrente
    ]
    trans_ricorrenti_mese_corrente = genera_occorrenze_da_regole(
        primo_giorno_mese_corrente, ultimo_giorno_mese_corrente
    )
    trans_totali_mese_corrente = (
        trans_reali_mese_corrente + trans_ricorrenti_mese_corrente
    )
    entrate_mese_corrente = sum(
        t.importo for t in trans_totali_mese_corrente if t.tipo == "entrata"
    )
    uscite_mese_corrente = sum(
        t.importo for t in trans_totali_mese_corrente if t.tipo == "uscita"
    )

    dati_grafici_torta = {
        "completo": {
            "entrate": entrate_attuali_totali,
            "uscite": uscite_attuali_totali,
        },
        "mese_corrente": {
            "entrate": entrate_mese_corrente,
            "uscite": uscite_mese_corrente,
            "nome_mese": nomi_mesi[today.month - 1],
        },
    }
    transazioni_reali_recenti = (
        Transazione.query.order_by(Transazione.data.desc()).limit(5).all()
    )

    return render_template(
        "index.html",
        saldo_attuale=saldo_attuale,
        saldo_fine_mese=saldo_fine_mese,
        prossimo_mese_info=prossimo_mese_info,
        transazioni=transazioni_reali_recenti,
        dati_grafici=dati_grafici_torta,
    )


# --- GESTIONE TRANSAZIONI ---

@app.route("/aggiungi", methods=["GET", "POST"])
def aggiungi_transazione():
    if request.method == "POST":
        categoria_id_form = request.form.get("categoria_id")
        importo_form = float(request.form["importo"])
        if importo_form < 0:
            flash("L'importo non può essere negativo.", "danger")
            return redirect(url_for("aggiungi_transazione"))
        nuova_transazione = Transazione(
            descrizione=request.form["descrizione"],
            importo=importo_form,
            tipo=request.form["tipo"],
            data=datetime.strptime(request.form["data"], "%Y-%m-%d").date(),
            categoria_id=int(categoria_id_form) if categoria_id_form else None,
        )
        db.session.add(nuova_transazione)
        db.session.commit()
        flash("Transazione aggiunta con successo!", "success")
        return redirect(url_for("lista_transazioni"))

    categorie = Categoria.query.order_by(Categoria.nome).all()
    return render_template(
        "aggiungi.html",
        data_default=date.today().strftime("%Y-%m-%d"),
        categorie=categorie,
    )


@app.route("/transazione/modifica/<int:transazione_id>", methods=["GET", "POST"])
def modifica_transazione(transazione_id):
    transazione = Transazione.query.get_or_404(transazione_id)
    if request.method == "POST":
        if transazione.importo < 0:
            flash("L'importo non può essere negativo.", "danger")
            return redirect(
                url_for("modifica_transazione", transazione_id=transazione_id)
            )
        transazione.descrizione = request.form["descrizione"]
        transazione.importo = float(request.form["importo"])
        transazione.tipo = request.form["tipo"]
        transazione.data = datetime.strptime(request.form["data"], "%Y-%m-%d").date()
        categoria_id_form = request.form.get("categoria_id")
        transazione.categoria_id = int(categoria_id_form) if categoria_id_form else None
        db.session.commit()
        flash("Transazione aggiornata con successo!", "success")
        return redirect(url_for("lista_transazioni"))

    categorie = Categoria.query.order_by(Categoria.nome).all()
    return render_template(
        "modifica_transazione.html", transazione=transazione, categorie=categorie
    )

# --- GESTIONE LISTA TRANSAZIONI ---

@app.route("/transazioni")
def lista_transazioni():
    today = date.today()

    # 1. Recupera i parametri dei filtri dall'URL. Se non ci sono, usa dei default.
    anno_selezionato = request.args.get("anno", default=today.year, type=int)
    tipo_selezionato = request.args.get("tipo", default="tutte", type=str)
    categoria_selezionata = request.args.get("categoria_id", default="tutte", type=str)
    query_ricerca = request.args.get("q", default="", type=str)

    # 2. Costruisci la query al database per le transazioni REALI in modo dinamico
    query_reale = Transazione.query

    # Filtro per anno
    if anno_selezionato != "tutti":
        query_reale = query_reale.filter(
            extract("year", Transazione.data) == anno_selezionato
        )

    # Filtro per tipo (entrata/uscita)
    if tipo_selezionato != "tutte":
        query_reale = query_reale.filter_by(tipo=tipo_selezionato)

    # Filtro per categoria
    if categoria_selezionata != "tutte":
        query_reale = query_reale.filter_by(categoria_id=int(categoria_selezionata))

    # Filtro per barra di ricerca (cerca nella descrizione)
    if query_ricerca:
        query_reale = query_reale.filter(
            Transazione.descrizione.ilike(f"%{query_ricerca}%")
        )

    elenco_reale = query_reale.all()

    # 3. Genera e filtra le transazioni RICORRENTI (in memoria, dopo la generazione)
    start_date_ricorrenti = (
        date(anno_selezionato, 1, 1)
        if anno_selezionato != "tutti"
        else date(today.year, 1, 1)
    )
    end_date_ricorrenti = (
        date(anno_selezionato, 12, 31)
        if anno_selezionato != "tutti"
        else date(today.year + 1, 12, 31)
    )

    elenco_ricorrente = genera_occorrenze_da_regole(
        start_date_ricorrenti, end_date_ricorrenti
    )

    if tipo_selezionato != "tutte":
        elenco_ricorrente = [t for t in elenco_ricorrente if t.tipo == tipo_selezionato]
    if query_ricerca:
        elenco_ricorrente = [
            t
            for t in elenco_ricorrente
            if query_ricerca.lower() in t.descrizione.lower()
        ]
    # Nota: il filtro per categoria sulle ricorrenti non è implementato

    # 4. Unisci e ordina i risultati
    elenco_completo = sorted(
        elenco_reale + elenco_ricorrente, key=lambda t: t.data, reverse=True
    )

    # 5. Prepara i dati da passare al template per popolare i filtri
    anni_disponibili = (
        db.session.query(extract("year", Transazione.data))
        .distinct()
        .order_by(extract("year", Transazione.data).desc())
        .all()
    )
    anni_disponibili = [a[0] for a in anni_disponibili if a[0] is not None]
    if not anni_disponibili or today.year not in anni_disponibili:
        anni_disponibili.append(today.year)

    tutte_le_categorie = Categoria.query.order_by(Categoria.nome).all()

    return render_template(
        "transazioni.html",
        elenco=elenco_completo,
        today=today,
        # Passiamo i valori attuali dei filtri per pre-compilare il form
        anni=sorted(list(set(anni_disponibili))),
        anno_selezionato=anno_selezionato,
        tipo_selezionato=tipo_selezionato,
        categorie=tutte_le_categorie,
        categoria_selezionata=(
            int(categoria_selezionata) if categoria_selezionata.isdigit() else "tutte"
        ),
        query_ricerca=query_ricerca,
    )


@app.route("/transazione/elimina/<int:transazione_id>", methods=["POST"])
def elimina_transazione(transazione_id):
    transazione = Transazione.query.get_or_404(transazione_id)
    db.session.delete(transazione)
    db.session.commit()
    flash("Transazione eliminata.", "success")
    return redirect(url_for("lista_transazioni"))

# --- GESTIONE RICORRENTI ---

@app.route("/ricorrenti")
def lista_ricorrenti():
    elenco = TransazioneRicorrente.query.order_by(
        TransazioneRicorrente.data_inizio.desc()
    ).all()
    return render_template("ricorrenti.html", elenco=elenco)


@app.route("/ricorrenti/aggiungi", methods=["GET", "POST"])
def aggiungi_ricorrente():
    if request.method == "POST":
        data_fine_str = request.form["data_fine"]
        importo_form = float(request.form["importo"])
        if importo_form < 0:
            flash("L'importo non può essere negativo.", "danger")
            return redirect(url_for("aggiungi_ricorrente"))
        data_fine = (
            datetime.strptime(data_fine_str, "%Y-%m-%d").date()
            if data_fine_str
            else None
        )
        nuova_regola = TransazioneRicorrente(
            descrizione=request.form["descrizione"],
            tipo=request.form["tipo"],
            importo=importo_form,
            frequenza=request.form["frequenza"],
            data_inizio=datetime.strptime(
                request.form["data_inizio"], "%Y-%m-%d"
            ).date(),
            data_fine=data_fine,
        )
        db.session.add(nuova_regola)
        db.session.commit()
        flash("Regola ricorrente aggiunta!", "success")
        return redirect(url_for("lista_ricorrenti"))
    return render_template("aggiungi_ricorrente.html")


@app.route("/ricorrenti/modifica/<int:regola_id>", methods=["GET", "POST"])
def modifica_ricorrente(regola_id):
    regola = TransazioneRicorrente.query.get_or_404(regola_id)
    if request.method == "POST":
        regola.descrizione = request.form["descrizione"]
        regola.importo = float(request.form["importo"])
        if regola.importo < 0:
            flash("L'importo non può essere negativo.", "danger")
            return redirect(url_for("modifica_ricorrente", regola_id=regola_id))
        regola.tipo = request.form["tipo"]
        regola.frequenza = request.form["frequenza"]
        regola.data_inizio = datetime.strptime(
            request.form["data_inizio"], "%Y-%m-%d"
        ).date()
        data_fine_str = request.form["data_fine"]
        regola.data_fine = (
            datetime.strptime(data_fine_str, "%Y-%m-%d").date()
            if data_fine_str
            else None
        )
        db.session.commit()
        flash("Regola ricorrente aggiornata!", "success")
        return redirect(url_for("lista_ricorrenti"))
    return render_template("modifica_ricorrente.html", regola=regola)


@app.route("/ricorrenti/rinnova/<int:regola_id>", methods=["POST"])
def rinnova_ricorrente(regola_id):
    regola = TransazioneRicorrente.query.get_or_404(regola_id)
    if regola.data_fine:
        regola.data_fine = regola.data_fine + relativedelta(years=1)
        db.session.commit()
        flash(
            f"Regola rinnovata fino al {regola.data_fine.strftime('%d/%m/%Y')}.",
            "success",
        )
    else:
        flash("Questa regola non ha una data di fine.", "warning")
    return redirect(url_for("lista_ricorrenti"))


@app.route("/ricorrenti/elimina/<int:regola_id>", methods=["POST"])
def elimina_ricorrente(regola_id):
    regola = TransazioneRicorrente.query.get_or_404(regola_id)
    db.session.delete(regola)
    db.session.commit()
    flash("Regola ricorrente eliminata.", "success")
    return redirect(url_for("lista_ricorrenti"))

# --- GESTIONE CATEGORIE ---

@app.route("/categorie")
def lista_categorie():
    elenco = Categoria.query.order_by(Categoria.nome).all()
    return render_template("categorie.html", elenco=elenco)


@app.route("/categorie/aggiungi", methods=["GET", "POST"])
def aggiungi_categoria():
    if request.method == "POST":
        nome_categoria = request.form["nome"]
        budget_str = request.form.get("budget_predefinito", "")
        if budget_str and float(budget_str) < 0:
            flash("Il budget non può essere negativo.", "danger")
            return redirect(url_for("aggiungi_categoria"))
        budget_predefinito = float(budget_str) if budget_str else None

        if not Categoria.query.filter_by(nome=nome_categoria).first():
            db.session.add(
                Categoria(nome=nome_categoria, budget_predefinito=budget_predefinito)
            )
            db.session.commit()
            flash("Categoria aggiunta.", "success")
        else:
            flash("Una categoria con questo nome esiste già.", "warning")
        return redirect(url_for("lista_categorie"))
    return render_template("aggiungi_categoria.html")


@app.route("/categorie/modifica/<int:categoria_id>", methods=["GET", "POST"])
def modifica_categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    if request.method == "POST":
        categoria.nome = request.form["nome"]
        budget_str = request.form.get("budget_predefinito", "")
        if budget_str and float(budget_str) < 0:
            flash("Il budget non può essere negativo.", "danger")
            return redirect(url_for("modifica_categoria", categoria_id=categoria_id))
        categoria.budget_predefinito = float(budget_str) if budget_str else None
        db.session.commit()
        flash("Categoria aggiornata.", "success")
        return redirect(url_for("lista_categorie"))
    return render_template("modifica_categoria.html", categoria=categoria)


@app.route("/categorie/elimina/<int:categoria_id>", methods=["POST"])
def elimina_categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    db.session.delete(categoria)
    db.session.commit()
    flash("Categoria eliminata.", "success")
    return redirect(url_for("lista_categorie"))

# --- GESTIONE RIEPILOGO ---

@app.route("/riepilogo", defaults={"anno_url": None})
@app.route("/riepilogo/<int:anno_url>")
def riepilogo_mensile(anno_url):
    today = date.today()
    anno_selezionato = anno_url if anno_url is not None else today.year
    anni_disponibili = [today.year + i for i in range(-2, 3)]

    start_of_year = date(anno_selezionato, 1, 1)
    end_of_year = date(anno_selezionato, 12, 31)

    transazioni_reali_anno = Transazione.query.filter(
        extract("year", Transazione.data) == anno_selezionato
    ).all()
    transazioni_ricorrenti_anno = genera_occorrenze_da_regole(
        start_of_year, end_of_year
    )
    transazioni_totali_anno = transazioni_reali_anno + transazioni_ricorrenti_anno

    nomi_mesi = [
        "Gennaio",
        "Febbraio",
        "Marzo",
        "Aprile",
        "Maggio",
        "Giugno",
        "Luglio",
        "Agosto",
        "Settembre",
        "Ottobre",
        "Novembre",
        "Dicembre",
    ]
    dati_mensili = []

    for mese_num in range(1, 13):
        transazioni_del_mese = sorted(
            [t for t in transazioni_totali_anno if t.data.month == mese_num],
            key=lambda x: x.data,
        )
        entrate = sum(t.importo for t in transazioni_del_mese if t.tipo == "entrata")
        uscite = sum(t.importo for t in transazioni_del_mese if t.tipo == "uscita")

        spese_mese_per_cat = defaultdict(float)
        uscite_del_mese_reali = [
            t
            for t in transazioni_del_mese
            if t.tipo == "uscita" and isinstance(t.id, int) and t.categoria
        ]
        for t in uscite_del_mese_reali:
            spese_mese_per_cat[t.categoria.nome] += t.importo

        dati_mensili.append(
            {
                "numero_mese": mese_num,
                "nome_mese": nomi_mesi[mese_num - 1],
                "entrate": entrate,
                "uscite": uscite,
                "saldo": entrate - uscite,
                "transazioni": transazioni_del_mese,
                "spese_per_categoria": dict(spese_mese_per_cat),
            }
        )

    # --- SPESE TOTALI PER CATEGORIA PER L'INTERO ANNO ---
    spese_anno_per_categoria = defaultdict(float)
    uscite_anno_reali = [
        t
        for t in transazioni_totali_anno
        if t.tipo == "uscita" and isinstance(t.id, int) and t.categoria
    ]
    for t in uscite_anno_reali:
        spese_anno_per_categoria[t.categoria.nome] += t.importo

    return render_template(
        "riepilogo.html",
        dati_mensili=dati_mensili,
        anno_selezionato=anno_selezionato,
        anni=anni_disponibili,
        spese_anno_per_categoria=dict(spese_anno_per_categoria),
    )

# --- GESTIONE BUDGET ---

@app.route("/budget", methods=["GET", "POST"])
def budget():
    today = date.today()

    # 1. Determina il mese e l'anno da visualizzare
    mese_anno_selezionato = request.args.get(
        "mese_anno", default=today.strftime("%Y-%m")
    )
    anno = int(mese_anno_selezionato.split("-")[0])
    mese = int(mese_anno_selezionato.split("-")[1])

    # 2. Logica per salvare i dati (invariata)
    if request.method == "POST":
        for key, value in request.form.items():
            if key.startswith("budget-"):
                if value and float(value) < 0:
                    flash("Il budget non può essere un valore negativo.", "danger")
                    # Ricostruisci l'URL per il redirect
                    mese_anno = request.args.get(
                        "mese_anno", default=date.today().strftime("%Y-%m")
                    )
                    return redirect(url_for("budget", mese_anno=mese_anno))
                cat_id = int(key.split("-")[1])
                budget_esistente = Budget.query.filter_by(
                    categoria_id=cat_id, mese=mese, anno=anno
                ).first()

                if value:
                    limite = float(value)
                    if budget_esistente:
                        budget_esistente.importo_limite = limite
                    else:
                        db.session.add(
                            Budget(
                                categoria_id=cat_id,
                                importo_limite=limite,
                                mese=mese,
                                anno=anno,
                            )
                        )
                elif budget_esistente:
                    db.session.delete(budget_esistente)

        db.session.commit()
        flash("Budget salvato con successo!", "success")
        return redirect(url_for("budget", mese_anno=f"{anno}-{mese:02d}"))

    # 3. Logica per preparare e visualizzare i dati (versione corretta)

    categorie = Categoria.query.order_by(Categoria.nome).all()

    # Definisci i periodi di tempo
    start_of_selected_month = date(anno, mese, 1)
    end_of_selected_month = start_of_selected_month + relativedelta(months=1, days=-1)

    start_of_previous_month = start_of_selected_month - relativedelta(months=1)
    end_of_previous_month = start_of_selected_month - relativedelta(days=1)

    # Funzione interna per raggruppare le spese per categoria in un dato periodo
    def calcola_spese_periodo(start_date, end_date):
        trans_reali = Transazione.query.filter(
            Transazione.tipo == "uscita", Transazione.data.between(start_date, end_date)
        ).all()
        trans_ricorrenti = [
            t
            for t in genera_occorrenze_da_regole(start_date, end_date)
            if t.tipo == "uscita"
        ]
        spese_totali = trans_reali + trans_ricorrenti

        spese_per_cat = defaultdict(float)
        for t in spese_totali:
            if (
                isinstance(t.id, int) and t.categoria_id
            ):  # Solo le transazioni reali possono avere categorie
                spese_per_cat[t.categoria_id] += t.importo
        return spese_per_cat

    # Calcola le spese per il mese selezionato e per quello precedente
    spese_per_categoria_selezionato = calcola_spese_periodo(
        start_of_selected_month, end_of_selected_month
    )
    spese_per_cat_mese_prec = calcola_spese_periodo(
        start_of_previous_month, end_of_previous_month
    )

    # Prepara la struttura dati completa da passare al template
    dati_budget = []
    for cat in categorie:
        override = Budget.query.filter_by(
            categoria_id=cat.id, mese=mese, anno=anno
        ).first()
        limite_effettivo = (
            override.importo_limite if override else cat.budget_predefinito or 0
        )

        speso_corrente = spese_per_categoria_selezionato.get(cat.id, 0)
        spesa_prec = spese_per_cat_mese_prec.get(cat.id, 0)

        dati_budget.append(
            {
                "categoria": cat,
                "limite_override": override.importo_limite if override else None,
                "limite_effettivo": limite_effettivo,
                "speso": speso_corrente,
                "rimanente": limite_effettivo - speso_corrente,
                "spesa_precedente": spesa_prec,
            }
        )

    return render_template(
        "budget.html",
        dati_budget=dati_budget,
        mese_anno_selezionato=mese_anno_selezionato,
    )

# --- GESTIONE ESPORTAZIONE DATI ---

@app.route("/esporta/csv/<int:anno>")
def esporta_csv(anno):
    """Genera ed esporta i dati dell'anno selezionato in formato CSV."""
    start_of_year = date(anno, 1, 1)
    end_of_year = date(anno, 12, 31)

    # Recupera tutti i dati dell'anno, proprio come facciamo nel riepilogo
    transazioni_reali = Transazione.query.filter(
        extract("year", Transazione.data) == anno
    ).all()
    transazioni_ricorrenti = genera_occorrenze_da_regole(start_of_year, end_of_year)
    elenco_completo = sorted(
        transazioni_reali + transazioni_ricorrenti, key=lambda t: t.data
    )

    # Usa un buffer di memoria per scrivere il CSV senza creare un file sul server
    output = io.StringIO()
    writer = csv.writer(output)

    # Scrivi l'intestazione
    writer.writerow(["Data", "Descrizione", "Tipo", "Importo", "Categoria"])

    # Scrivi i dati
    for t in elenco_completo:
        categoria = t.categoria.nome if isinstance(t.id, int) and t.categoria else ""
        writer.writerow(
            [t.data.strftime("%Y-%m-%d"), t.descrizione, t.tipo, t.importo, categoria]
        )

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=riepilogo_{anno}.csv"},
    )

@app.route("/esporta/pdf/<int:anno>")
def esporta_pdf(anno):
    """Genera un report PDF per l'anno selezionato."""
    start_of_year = date(anno, 1, 1)
    end_of_year = date(anno, 12, 31)

    transazioni_reali = Transazione.query.filter(
        extract("year", Transazione.data) == anno
    ).all()
    transazioni_ricorrenti = genera_occorrenze_da_regole(start_of_year, end_of_year)
    elenco_completo = sorted(
        transazioni_reali + transazioni_ricorrenti, key=lambda t: t.data
    )

    # Calcola i totali
    tot_entrate = sum(t.importo for t in elenco_completo if t.tipo == "entrata")
    tot_uscite = sum(t.importo for t in elenco_completo if t.tipo == "uscita")

    # Renderizza un template HTML specifico per il PDF
    html_per_pdf = render_template(
        "report_pdf.html",
        elenco=elenco_completo,
        anno=anno,
        tot_entrate=tot_entrate,
        tot_uscite=tot_uscite,
        saldo_finale=tot_entrate - tot_uscite,
    )

    # Converte l'HTML in PDF usando WeasyPrint
    pdf = HTML(string=html_per_pdf).write_pdf()

    return Response(
        pdf,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"inline;filename=riepilogo_{anno}.pdf"},
    )

@app.route("/esporta/csv/<int:anno>/<int:mese>")
def esporta_csv_mensile(anno, mese):
    """Genera ed esporta i dati di un mese specifico in formato CSV."""
    start_of_month = date(anno, mese, 1)
    end_of_month = start_of_month + relativedelta(months=1, days=-1)

    transazioni_reali = Transazione.query.filter(
        Transazione.data >= start_of_month, Transazione.data <= end_of_month
    ).all()
    transazioni_ricorrenti = genera_occorrenze_da_regole(start_of_month, end_of_month)
    elenco_completo = sorted(
        transazioni_reali + transazioni_ricorrenti, key=lambda t: t.data
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Data", "Descrizione", "Tipo", "Importo", "Categoria"])
    for t in elenco_completo:
        categoria = t.categoria.nome if isinstance(t.id, int) and t.categoria else ""
        writer.writerow(
            [t.data.strftime("%Y-%m-%d"), t.descrizione, t.tipo, t.importo, categoria]
        )
    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment;filename=riepilogo_{anno}-{mese:02d}.csv"
        },
    )

@app.route("/esporta/pdf/<int:anno>/<int:mese>")
def esporta_pdf_mensile(anno, mese):
    """Genera un report PDF per un mese specifico."""
    start_of_month = date(anno, mese, 1)
    end_of_month = start_of_month + relativedelta(months=1, days=-1)
    nomi_mesi = [
        "Gennaio",
        "Febbraio",
        "Marzo",
        "Aprile",
        "Maggio",
        "Giugno",
        "Luglio",
        "Agosto",
        "Settembre",
        "Ottobre",
        "Novembre",
        "Dicembre",
    ]
    nome_mese = nomi_mesi[mese - 1]

    transazioni_reali = Transazione.query.filter(
        Transazione.data >= start_of_month, Transazione.data <= end_of_month
    ).all()
    transazioni_ricorrenti = genera_occorrenze_da_regole(start_of_month, end_of_month)
    elenco_completo = sorted(
        transazioni_reali + transazioni_ricorrenti, key=lambda t: t.data
    )

    tot_entrate = sum(t.importo for t in elenco_completo if t.tipo == "entrata")
    tot_uscite = sum(t.importo for t in elenco_completo if t.tipo == "uscita")

    html_per_pdf = render_template(
        "report_pdf.html",
        elenco=elenco_completo,
        anno=anno,
        nome_mese=nome_mese,  # Passiamo il nome del mese
        tot_entrate=tot_entrate,
        tot_uscite=tot_uscite,
        saldo_finale=tot_entrate - tot_uscite,
    )

    pdf = HTML(string=html_per_pdf).write_pdf()

    return Response(
        pdf,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f"inline;filename=riepilogo_{anno}-{mese:02d}.pdf"
        },
    )

# --- GESTIONE ANALISI E GRAFICI ---

@app.route("/analisi")
def pagina_analisi():
    today = date.today()

    # --- MODIFICA 1: Orizzonte storico di 13 mesi ---
    numero_mesi_storico = 13
    start_date_storico = (today.replace(day=1)) - relativedelta(
        months=numero_mesi_storico - 1
    )

    storico_labels = []
    storico_dati_saldo = []

    tutte_le_transazioni_reali = (
        Transazione.query.filter(Transazione.data >= start_date_storico)
        .order_by(Transazione.data)
        .all()
    )
    tutte_le_categorie = Categoria.query.all()

    dati_categorie_per_mese = {
        cat.nome: [0.0] * numero_mesi_storico for cat in tutte_le_categorie
    }
    storico_entrate_mensili = [0.0] * numero_mesi_storico
    storico_uscite_mensili = [0.0] * numero_mesi_storico

    ricorrenti_storico = genera_occorrenze_da_regole(
        start_date_storico, today + relativedelta(months=1)
    )

    # Ciclo principale aggiornato per 13 mesi
    for i in range(numero_mesi_storico):
        mese_corrente_loop = start_date_storico + relativedelta(months=i)
        storico_labels.append(mese_corrente_loop.strftime("%b %y"))

        trans_reali_mese = [
            t
            for t in tutte_le_transazioni_reali
            if t.data.year == mese_corrente_loop.year
            and t.data.month == mese_corrente_loop.month
        ]
        trans_ricorrenti_mese = [
            t
            for t in ricorrenti_storico
            if t.data.year == mese_corrente_loop.year
            and t.data.month == mese_corrente_loop.month
        ]
        trans_totali_mese = trans_reali_mese + trans_ricorrenti_mese

        entrate_mese = sum(t.importo for t in trans_totali_mese if t.tipo == "entrata")
        uscite_mese = sum(t.importo for t in trans_totali_mese if t.tipo == "uscita")
        storico_entrate_mensili[i] = entrate_mese
        storico_uscite_mensili[i] = uscite_mese

        for t in trans_reali_mese:
            if t.tipo == "uscita" and t.categoria_id is not None:
                dati_categorie_per_mese[t.categoria.nome][i] += t.importo

    # Calcolo patrimonio (richiede un ciclo separato per essere cumulativo)
    tutte_trans_reali_storiche_complete = Transazione.query.order_by(
        Transazione.data
    ).all()
    for i in range(numero_mesi_storico):
        mese_corrente_loop = start_date_storico + relativedelta(months=i)
        fine_mese_loop = mese_corrente_loop.replace(day=1) + relativedelta(
            months=1, days=-1
        )
        trans_reali_fino_a_mese = [
            t for t in tutte_trans_reali_storiche_complete if t.data <= fine_mese_loop
        ]
        ricorrenti_fino_a_mese = genera_occorrenze_da_regole(
            date(2000, 1, 1), fine_mese_loop
        )
        entrate = sum(
            t.importo
            for t in (trans_reali_fino_a_mese + ricorrenti_fino_a_mese)
            if t.tipo == "entrata"
        )
        uscite = sum(
            t.importo
            for t in (trans_reali_fino_a_mese + ricorrenti_fino_a_mese)
            if t.tipo == "uscita"
        )
        storico_dati_saldo.append(round(entrate - uscite, 2))

    # Calcolo previsioni prossimo mese (invariato)
    prossimo_mese_inizio = today.replace(day=1) + relativedelta(months=1)
    prossimo_mese_fine = prossimo_mese_inizio + relativedelta(months=1, days=-1)
    trans_reali_prossimo_mese = Transazione.query.filter(
        Transazione.data >= prossimo_mese_inizio, Transazione.data <= prossimo_mese_fine
    ).all()
    trans_ricorrenti_prossimo_mese = genera_occorrenze_da_regole(
        prossimo_mese_inizio, prossimo_mese_fine
    )
    trans_totali_prossimo_mese = (
        trans_reali_prossimo_mese + trans_ricorrenti_prossimo_mese
    )
    entrate_previste_mese_dopo = sum(
        t.importo for t in trans_totali_prossimo_mese if t.tipo == "entrata"
    )
    uscite_previste_mese_dopo = sum(
        t.importo for t in trans_totali_prossimo_mese if t.tipo == "uscita"
    )

    storico_labels.append(prossimo_mese_inizio.strftime("%b %y (Prev)"))
    storico_entrate_mensili.append(entrate_previste_mese_dopo)
    storico_uscite_mensili.append(uscite_previste_mese_dopo)

    # Formattazione per Chart.js (invariata)
    colori_grafico = [
        "#FF6384",
        "#36A2EB",
        "#FFCE56",
        "#4BC0C0",
        "#9966FF",
        "#FF9F40",
        "#C9CBCF",
    ]
    storico_categorie_datasets = []
    for i, (nome_cat, dati) in enumerate(dati_categorie_per_mese.items()):
        if sum(dati) > 0:
            storico_categorie_datasets.append(
                {
                    "label": nome_cat,
                    "data": dati,
                    "borderColor": colori_grafico[i % len(colori_grafico)],
                    "tension": 0.1,
                    "fill": False,
                }
            )

    return render_template(
        "analisi.html",
        storico_labels=storico_labels,
        storico_dati_saldo=storico_dati_saldo,
        storico_categorie_datasets=storico_categorie_datasets,
        storico_entrate_mensili=storico_entrate_mensili,
        storico_uscite_mensili=storico_uscite_mensili,
    )