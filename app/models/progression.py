from app.extension import db
from app.models.base import BaseModel

class Progression(BaseModel):
    __tablename__ = 'progressions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sourate = db.Column(db.String(100), nullable=False)
    nombre_versets = db.Column(db.Integer, nullable=False)
    date_evaluation = db.Column(db.Date, nullable=False)
    observations = db.Column(db.Text, nullable=True)

    talibe_matricule = db.Column(db.String(50), db.ForeignKey('talibes.matricule'), nullable=False)