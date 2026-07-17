from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired, Length


# --- FORMULAIRE MAÎTRE ---
class MaitreForm(FlaskForm):
    matricule = StringField('Matricule', validators=[DataRequired(message="Matricule obligatoire"), Length(max=50)])
    prenom = StringField('Prénom', validators=[DataRequired(message="Prenom  obligatoire"), Length(max=100)])
    nom = StringField('Nom', validators=[DataRequired(message="Nom  obligatoire"), Length(max=100)])
    telephone = StringField('Téléphone', validators=[DataRequired(message="Téléphone obligatoire"), Length(max=20)])
    submit = SubmitField('Enregistrer')

