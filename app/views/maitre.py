from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extension import db
from app.models.maitre import Maitre
from app.forms.maitre import MaitreForm  # Votre formulaire WTForms pour le maître
from app.exceptions import (
    DaaraException,
    MaitreIntrouvableException,
    MaitreDejaExistantException,
    SuppressionImpossibleException
)

bp_maitres = Blueprint('maitres', __name__, url_prefix='/maitres')


@bp_maitres.route('/')
def lister():
    q = request.args.get('q', '').strip()
    query = Maitre.query

    if q:
        query = query.filter(
            Maitre.nom.ilike(f'%{q}%') | Maitre.prenom.ilike(f'%{q}%')
        )

    maitres = query.order_by(Maitre.nom).all()
    return render_template('maitres/liste.html', maitres=maitres, q=q)


@bp_maitres.route('/nouveau', methods=['GET', 'POST'])
def creer():
    form = MaitreForm()

    if form.validate_on_submit():
        try:
            # 1. Vérification si le maître existe déjà
            if db.session.get(Maitre, form.matricule.data):
                raise MaitreDejaExistantException(form.matricule.data)

            # 2. Création de l'entité
            maitre = Maitre(
                matricule=form.matricule.data,
                prenom=form.prenom.data,
                nom=form.nom.data,
                telephone=form.telephone.data
            )

            db.session.add(maitre)
            db.session.commit()

            flash('Maître ajouté avec succès.', 'success')
            return redirect(url_for('maitres.lister'))

        except DaaraException as e:
            db.session.rollback()
            flash(str(e), 'danger')
            return render_template('maitres/formulaire.html', form=form), 400

    return render_template('maitres/formulaire.html', form=form, maitre=None)


@bp_maitres.route('/<matricule>/supprimer', methods=['POST'])
def supprimer(matricule):
    try:
        maitre = db.session.get(Maitre, matricule)

        # 1. Vérifier si le maître existe
        if not maitre:
            raise MaitreIntrouvableException(matricule)

        # 2. Règle métier : Interdiction de supprimer s'il encadre des classes
        if len(maitre.classes) > 0:
            raise SuppressionImpossibleException(
                f"Le maître {maitre.prenom} {maitre.nom} encadre actuellement {len(maitre.classes)} classe(s). "
                "Veuillez réassigner ou supprimer ces classes avant de pouvoir le retirer."
            )

        db.session.delete(maitre)
        db.session.commit()
        flash('Maître supprimé avec succès.', 'success')

    except DaaraException as e:
        db.session.rollback()
        # Le message exact de l'exception est intercepté ici et envoyé au template via flash()
        flash(str(e), 'danger')

    return redirect(url_for('maitres.lister'))