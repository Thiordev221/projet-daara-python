from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


# --- FORMULAIRE PROGRESSION ---
class ProgressionForm(FlaskForm):
    sourate = StringField('Sourate', validators=[DataRequired(message="Sourate obligatoire"), Length(max=100)])
    nombre_versets = IntegerField('Nombre de versets', validators=[
        DataRequired(message="Veuillez entrer un nombre."),
        NumberRange(min=0, message="Le nombre de versets doit être positif.")
    ])
    date_evaluation = DateField("Date d'évaluation", validators=[DataRequired(message="Date obligatoire")])
    observations = TextAreaField('Observations / Remarques', validators=[Optional()])

    # Alimenté dynamiquement dans la vue depuis la table 'talibes'
    talibe_matricule = SelectField('Talibé', validators=[DataRequired(message="Talibe obligatoire")])

    submit = SubmitField('Enregistrer')