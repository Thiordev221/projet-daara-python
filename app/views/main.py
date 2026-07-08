from flask import Blueprint, render_template

bp_main = Blueprint("main", __name__)

@bp_main.route("/")
def accueil():
    return "<h1>hello<h1>"

@bp_main.route("/contact")
def contact():
    return "Salut"