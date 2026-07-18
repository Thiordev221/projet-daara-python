from app.extension import db
from app.models.base import BaseModel

# On importe BaseModel

class Talibe(BaseModel):  # Hérite de BaseModel
    __tablename__ = "talibes"

    # Clé saisie par l'utilisateur
    matricule = db.Column(db.String(50), primary_key=True)
    prenom = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date)
    nom_tuteur = db.Column(db.String(200))
    telephone_tuteur = db.Column(db.String(20))

    # Finir de compléter la classe avec la relation obligatoire
    classe_code = db.Column(db.String(50), db.ForeignKey('classes.code'), nullable=False)
    progressions = db.relationship('Progression', backref='talibe', cascade='all, delete-orphan' , lazy=True)