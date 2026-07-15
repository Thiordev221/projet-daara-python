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


@bp_talibes.route('/<matricule>/modifier', methods=['GET', 'POST'])
def modifier(matricule):
    talibe = db.session.get(Talibe, matricule)
    if not talibe:
        raise TalibeIntrouvableException(matricule)

    # On pré-remplit le formulaire avec les données actuelles du talibé
    form = TalibeForm(obj=talibe)

    # Alimentation dynamique des classes
    form.classe_code.choices = [(c.code, c.libelle) for c in Classe.query.order_by(Classe.libelle).all()]

    # Désactiver le champ matricule pour empêcher sa modification
    if request.method == 'GET':
        form.matricule.data = talibe.matricule

    if form.validate_on_submit():
        try:
            # Mise à jour des champs
            talibe.prenom = form.prenom.data
            talibe.nom = form.nom.data
            talibe.date_naissance = form.date_naissance.data
            talibe.nom_tuteur = form.nom_tuteur.data
            talibe.telephone_tuteur = form.telephone_tuteur.data
            talibe.classe_code = form.classe_code.data

            db.session.commit()
            flash('Informations du talibé mises à jour.', 'success')
            return redirect(url_for('talibes.lister'))

        except DaaraException as e:
            db.session.rollback()
            flash(str(e), 'danger')
            return render_template('talibes/formulaire_modifier.html', form=form, talibe=talibe), 400

    # On passe l'objet 'talibe' au template pour savoir qu'on est en mode édition
    return render_template('talibes/formulaire_modifier.html', form=form, talibe=talibe)

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


import csv
from io import StringIO
from flask import Response


@bp_talibes.route('/exporter')
def exporter_csv():
    # 1. Récupérer les données de la base
    talibes = Talibe.query.order_by(Talibe.nom).all()

    # 2. Créer un flux d'écriture en mémoire
    flux = StringIO()

    # Écriture du BOM UTF-8 pour forcer Excel à lire correctement les accents (é, è, à...)
    flux.write('\ufeff')

    # Initialisation du writer CSV avec le point-virgule comme délimiteur
    writer = csv.writer(flux, delimiter=';')

    # 3. Écrire la ligne d'en-tête
    writer.writerow([
        'Matricule',
        'Prénom',
        'Nom',
        'Date de Naissance',
        'Classe',
        'Tuteur',
        'Téléphone Tuteur'
    ])

    # 4. Écrire les lignes de données
    for t in talibes:
        date_naiss = t.date_naissance.strftime('%d/%m/%Y') if t.date_naissance else 'Non renseignée'
        classe_libelle = t.classe.libelle if t.classe else 'Sans classe'

        writer.writerow([
            t.matricule,
            t.prenom,
            t.nom,
            date_naiss,
            classe_libelle,
            t.nom_tuteur or '',
            t.telephone_tuteur or ''
        ])

    # 5. Préparer la réponse Flask pour le téléchargement
    reponse_contenu = flux.getvalue()
    flux.close()

    return Response(
        reponse_contenu,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=export_talibes.csv",
            "Cache-Control": "no-cache"
        }
    )