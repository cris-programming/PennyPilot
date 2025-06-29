from app import db
from datetime import datetime


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    transazioni = db.relationship("Transazione", backref="categoria", lazy=True)
    budget_predefinito = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"Categoria('{self.nome}')"


class Transazione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descrizione = db.Column(db.String(100), nullable=False)
    importo = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(7), nullable=False)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=True)

    def __repr__(self):
        return f"Transazione('{self.descrizione}', '{self.importo}')"


class TransazioneRicorrente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descrizione = db.Column(db.String(100), nullable=False)
    importo = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(7), nullable=False)
    data_inizio = db.Column(db.Date, nullable=False)
    data_fine = db.Column(db.Date, nullable=True)
    frequenza = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Ricorrenza('{self.descrizione}', '{self.importo}')"


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    importo_limite = db.Column(db.Float, nullable=False)
    mese = db.Column(db.Integer, nullable=False)
    anno = db.Column(db.Integer, nullable=False)

    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)

    # Questo assicura che non si possa avere più di un budget per la stessa categoria nello stesso mese/anno
    __table_args__ = (
        db.UniqueConstraint("categoria_id", "mese", "anno", name="_cat_mese_anno_uc"),
    )

    def __repr__(self):
        return (
            f"Budget('{self.importo_limite}', Mese: '{self.mese}', Anno: '{self.anno}')"
        )
