from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extension import db
from app.models.talibe import Talibe
from app.models.classe import Classe
from app.forms.talibe import TalibeForm  # Assurez-vous que votre formulaire est bien ici
from app.exceptions import (
    DaaraException,
    TalibeDejaExistantException,
    TalibeIntrouvableException
)

# Déclaration du Blueprint
bp_talibes = Blueprint('talibes', __name__, url_prefix='/talibes')


@bp_talibes.route('/')
def lister():
    q = request.args.get('q', '').strip()
    classe_code = request.args.get('classe', '').strip()

    query = Talibe.query

    if classe_code:
        query = query.filter_by(classe_code=classe_code)
    if q:
        query = query.filter(
            Talibe.nom.ilike(f'%{q}%') | Talibe.prenom.ilike(f'%{q}%')
        )

    talibes = query.order_by(Talibe.nom).all()
    classes = Classe.query.order_by(Classe.libelle).all()

    return render_template('talibes/liste.html', talibes=talibes, classes=classes, q=q)


@bp_talibes.route('/nouveau', methods=['GET', 'POST'])
def creer():
    form = TalibeForm()

    # Alimentation dynamique du SelectField depuis la BDD
    form.classe_code.choices = [(c.code, c.libelle) for c in Classe.query.order_by(Classe.libelle).all()]

    if form.validate_on_submit():
        try:
            # 1. Vérification si le talibé existe déjà
            if db.session.get(Talibe, form.matricule.data):
                raise TalibeDejaExistantException(form.matricule.data)

            # 2. Création de l'entité avec TOUS les champs requis par le modèle
            talibe = Talibe(
                matricule=form.matricule.data,
                prenom=form.prenom.data,
                nom=form.nom.data,
                date_naissance=form.date_naissance.data,
                nom_tuteur=form.nom_tuteur.data,
                telephone_tuteur=form.telephone_tuteur.data,
                classe_code=form.classe_code.data
            )

            db.session.add(talibe)
            db.session.commit()

            flash('Talibé ajouté avec succès.', 'success')
            return redirect(url_for('talibes.lister'))

        except DaaraException as e:
            # On intercepte l'exception, on annule la session et on flash l'erreur
            db.session.rollback()
            flash(str(e), 'danger')
            # On réaffiche le formulaire en conservant les saisies de l'utilisateur
            return render_template('talibes/formulaire.html', form=form, talibe=None), 400

    return render_template('talibes/formulaire.html', form=form, talibe=None)


@bp_talibes.route('/<matricule>/supprimer', methods=['POST'])
def supprimer(matricule):
    try:
        talibe = db.session.get(Talibe, matricule)

        # Si le talibé n'existe pas, on lève l'exception dédiée
        if not talibe:
            raise TalibeIntrouvableException(matricule)

        db.session.delete(talibe)  # La cascade configurée gère la suppression des progressions
        db.session.commit()
        flash('Talibé supprimé avec succès.', 'success')

    except DaaraException as e:
        db.session.rollback()
        flash(str(e), 'danger')

    return redirect(url_for('talibes.lister'))