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


@bp_classes.route('/<code>/modifier', methods=['GET', 'POST'])
def modifier(code):
    classe = db.session.get(Classe, code)
    if not classe:
        raise ClasseIntrouvableException(code)

    form = ClasseForm(obj=classe)
    form.maitre_matricule.choices = [
        (m.matricule, f"{m.prenom} {m.nom}") for m in Maitre.query.order_by(Maitre.nom).all()
    ]

    if request.method == 'GET':
        form.code.data = classe.code

    if form.validate_on_submit():
        try:
            classe.libelle = form.libelle.data
            classe.niveau = form.niveau.data
            classe.maitre_matricule = form.maitre_matricule.data

            db.session.commit()
            flash('Classe mise à jour avec succès.', 'success')
            return redirect(url_for('classes.lister'))

        except DaaraException as e:
            db.session.rollback()
            flash(str(e), 'danger')
            return render_template('classes/formulaire_modifier.html', form=form, classe=classe), 400

    return render_template('classes/formulaire_modifier.html', form=form, classe=classe)

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


import csv
from io import StringIO
from flask import Response
from app.models.classe import Classe  # Assurez-vous d'importer votre modèle


# ... (vos autres imports et routes) ...

@bp_classes.route('/exporter')
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