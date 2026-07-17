from flask import Blueprint, render_template, url_for, request

from app.models.classe import Classe
from app.models.talibe import Talibe

bp_main = Blueprint("main", __name__)

@bp_main.route("/")
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
