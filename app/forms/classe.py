from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired, Length


# --- FORMULAIRE CLASSE ---
class ClasseForm(FlaskForm):
    code = StringField('Code Classe', validators=[DataRequired(), Length(max=50)])
    libelle = StringField('Libellé', validators=[DataRequired(), Length(max=100)])
    niveau = StringField('Niveau', validators=[DataRequired(), Length(max=50)])

    # Alimenté dynamiquement dans la vue depuis la table 'maitres'
    maitre_matricule = SelectField('Maître Responsable', validators=[DataRequired()])

    submit = SubmitField('Enregistrer')