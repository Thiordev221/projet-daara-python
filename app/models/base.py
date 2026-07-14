# app/extension.py
from datetime import datetime
from app.extension import db


# Voici la classe demandée par le prof
class BaseModel(db.Model):
    __abstract__ = True  # Ne pas créer de table pour cette classe

    # Colonnes communes automatiques
    cree_le = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    maj_le = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)