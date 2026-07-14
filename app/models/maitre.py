from app.extension import db
from app.models.base import BaseModel


class Maitre(BaseModel):
    __tablename__ = 'maitres'

    matricule = db.Column(db.String(50), primary_key=True)
    prenom = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)

    classes = db.relationship('Classe', backref='maitre', lazy=True)