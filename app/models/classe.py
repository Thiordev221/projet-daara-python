from app.extension import db
from app.models.base import BaseModel


class Classe(BaseModel):
    __tablename__ = 'classes'

    code = db.Column(db.String(50), primary_key=True)
    libelle = db.Column(db.String(100), nullable=False)
    niveau = db.Column(db.String(50), nullable=False)

    maitre_matricule = db.Column(db.String(50), db.ForeignKey('maitres.matricule'), nullable=False)
    talibes = db.relationship('Talibe', backref='classe', lazy=True)