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


@bp_maitres.route('/<matricule>/modifier', methods=['GET', 'POST'])
def modifier(matricule):
    maitre = db.session.get(Maitre, matricule)
    if not maitre:
        raise MaitreIntrouvableException(matricule)

    form = MaitreForm(obj=maitre)

    if request.method == 'GET':
        form.matricule.data = maitre.matricule

    if form.validate_on_submit():
        try:
            maitre.prenom = form.prenom.data
            maitre.nom = form.nom.data
            maitre.telephone = form.telephone.data

            db.session.commit()
            flash('Informations du maître mises à jour.', 'success')
            return redirect(url_for('maitres.lister'))

        except DaaraException as e:
            db.session.rollback()
            flash(str(e), 'danger')
            return render_template('maitres/formulaire_modifier.html', form=form, maitre=maitre)

    return render_template('maitres/formulaire_modifier.html', form=form, maitre=maitre)

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


import csv
from io import StringIO
from flask import Response
from app.models.classe import Classe  # Assurez-vous d'importer votre modèle


# ... (vos autres imports et routes) ...

@bp_maitres.route('/exporter')
def exporter_csv():
    # 1. Récupérer les classes
    classes = Classe.query.order_by(Classe.libelle).all()

    # 2. Créer le flux mémoire
    flux = StringIO()
    flux.write('\ufeff')  # BOM UTF-8 pour Excel

    writer = csv.writer(flux, delimiter=';')

    # 3. En-tête du fichier CSV
    writer.writerow([
        'Code Classe',
        'Libellé',
        'Niveau',
        'Maître Responsable',
        'Nombre de Talibés'
    ])

    # 4. Écriture des lignes
    for c in classes:
        nom_maitre = f"{c.maitre.prenom} {c.maitre.nom}" if c.maitre else "Aucun"
        nb_talibes = len(c.talibes) if c.talibes else 0

        writer.writerow([
            c.code,
            c.libelle,
            c.niveau,
            nom_maitre,
            nb_talibes
        ])

    reponse_contenu = flux.getvalue()
    flux.close()

    return Response(
        reponse_contenu,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=export_classes.csv",
            "Cache-Control": "no-cache"
        }
    )