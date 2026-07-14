from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extension import db
from app.models.progression import Progression
from app.models.talibe import Talibe
from app.forms.progression import ProgressionForm  # Assurez-vous d'avoir créé ce formulaire
from app.exceptions import (
    DaaraException,
    ProgressionIntrouvableException,
    ProgressionInvalideException
)

bp_progressions = Blueprint('progressions', __name__, url_prefix='/progressions')


@bp_progressions.route('/')
def lister():
    # Optionnel : Filtrer les progressions par talibé si nécessaire
    talibe_matricule = request.args.get('talibe')
    if talibe_matricule:
        progressions = Progression.query.filter_by(talibe_matricule=talibe_matricule).all()
    else:
        progressions = Progression.query.order_by(Progression.date_evaluation.desc()).all()

    return render_template('progressions/liste.html', progressions=progressions)


@bp_progressions.route('/nouveau', methods=['GET', 'POST'])
def creer():
    form = ProgressionForm()
    # Alimentation dynamique : on liste les talibés pour que l'utilisateur choisisse
    form.talibe_matricule.choices = [
        (t.matricule, f"{t.prenom} {t.nom}") for t in Talibe.query.order_by(Talibe.nom).all()
    ]

    if form.validate_on_submit():
        try:
            # 1. Validation métier (Consigne : lever ProgressionInvalideException)
            if form.nombre_versets.data < 0:
                raise ProgressionInvalideException("Le nombre de versets ne peut pas être négatif.")

            if not form.sourate.data or len(form.sourate.data.strip()) == 0:
                raise ProgressionInvalideException("La sourate ne peut pas être vide.")

            # Vérifier si le talibé existe vraiment
            if not db.session.get(Talibe, form.talibe_matricule.data):
                raise ProgressionInvalideException("Le talibé sélectionné n'existe pas.")

            # 2. Création
            progression = Progression(
                sourate=form.sourate.data,
                nombre_versets=form.nombre_versets.data,
                date_evaluation=form.date_evaluation.data,
                observations=form.observations.data,
                talibe_matricule=form.talibe_matricule.data
            )

            db.session.add(progression)
            db.session.commit()

            flash('Progression enregistrée avec succès.', 'success')
            return redirect(url_for('progressions.lister'))

        except DaaraException as e:
            db.session.rollback()
            flash(str(e), 'danger')
            return render_template('progressions/formulaire.html', form=form), 400

    return render_template('progressions/formulaire.html', form=form)


@bp_progressions.route('/<int:id>/supprimer', methods=['POST'])
def supprimer(id):
    try:
        progression = db.session.get(Progression, id)
        if not progression:
            raise ProgressionIntrouvableException(id)

        db.session.delete(progression)
        db.session.commit()
        flash('Progression supprimée.', 'success')

    except DaaraException as e:
        db.session.rollback()
        flash(str(e), 'danger')

    return redirect(url_for('progressions.lister'))