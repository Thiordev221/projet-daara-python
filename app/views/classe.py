from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extension import db
from app.models.classe import Classe
from app.models.maitre import Maitre
from app.forms.classe import ClasseForm  # Votre formulaire WTForms pour la classe
from app.exceptions import (
    DaaraException,
    ClasseIntrouvableException,
    ClasseDejaExistanteException,
    SuppressionImpossibleException
)

bp_classes = Blueprint('classes', __name__, url_prefix='/classes')


@bp_classes.route('/')
def lister():
    q = request.args.get('q', '').strip()
    query = Classe.query

    if q:
        query = query.filter(
            Classe.libelle.ilike(f'%{q}%') | Classe.code.ilike(f'%{q}%')
        )

    classes = query.order_by(Classe.libelle).all()
    return render_template('classes/liste.html', classes=classes, q=q)


@bp_classes.route('/nouveau', methods=['GET', 'POST'])
def creer():
    form = ClasseForm()

    # Alimentation dynamique du SelectField avec les maîtres disponibles
    form.maitre_matricule.choices = [
        (m.matricule, f"{m.prenom} {m.nom}") for m in Maitre.query.order_by(Maitre.nom).all()
    ]

    if form.validate_on_submit():
        try:
            # 1. Vérification si la classe existe déjà
            if db.session.get(Classe, form.code.data):
                raise ClasseDejaExistanteException(form.code.data)

            # 2. Création de la classe
            classe = Classe(
                code=form.code.data,
                libelle=form.libelle.data,
                niveau=form.niveau.data,
                maitre_matricule=form.maitre_matricule.data
            )

            db.session.add(classe)
            db.session.commit()

            flash('Classe créée avec succès.', 'success')
            return redirect(url_for('classes.lister'))

        except DaaraException as e:
            db.session.rollback()
            flash(str(e), 'danger')
            return render_template('classes/formulaire.html', form=form), 400

    return render_template('classes/formulaire.html', form=form, classe=None)


@bp_classes.route('/<code>/supprimer', methods=['POST'])
def supprimer(code):
    try:
        classe = db.session.get(Classe, code)

        # 1. Vérifier si la classe existe
        if not classe:
            raise ClasseIntrouvableException(code)

        # 2. Règle métier : Interdit de supprimer une classe qui regroupe des talibés
        if len(classe.talibes) > 0:
            raise SuppressionImpossibleException(
                f"La classe '{classe.libelle}' contient actuellement {len(classe.talibes)} talibé(s). "
                "Veuillez transférer ces talibés dans une autre classe avant de pouvoir la supprimer."
            )

        db.session.delete(classe)
        db.session.commit()
        flash('Classe supprimée avec succès.', 'success')

    except DaaraException as e:
        db.session.rollback()
        flash(str(e), 'danger')

    return redirect(url_for('classes.lister'))