from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


# --- FORMULAIRE TALIBÉ ---
class TalibeForm(FlaskForm):
    matricule = StringField('Matricule', validators=[DataRequired(), Length(max=50)])
    prenom = StringField('Prénom', validators=[DataRequired(), Length(max=100)])
    nom = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    date_naissance = DateField('Date de naissance', validators=[Optional()])
    nom_tuteur = StringField('Nom du tuteur', validators=[Length(max=200)])
    telephone_tuteur = StringField('Téléphone tuteur', validators=[Length(max=20)])

    # Alimenté dynamiquement dans la vue depuis la table 'classes'
    classe_code = SelectField('Classe', validators=[DataRequired()])

    submit = SubmitField('Enregistrer')