from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired, Length


# --- FORMULAIRE MAÎTRE ---
class MaitreForm(FlaskForm):
    matricule = StringField('Matricule', validators=[DataRequired(), Length(max=50)])
    prenom = StringField('Prénom', validators=[DataRequired(), Length(max=100)])
    nom = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    telephone = StringField('Téléphone', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Enregistrer')

