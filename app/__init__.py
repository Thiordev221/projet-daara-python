from flask import Flask
from .extension import db, migrate
# from .models.classe import classe
# from .models.maitre import maitre
# from .models.progressiosn import prpogression
# from .models.talibe import talibes


def create_app(nom_config="dev"):
    app = Flask(__name__)
    app.config.from_object(
        f"config.{nom_config.capitalize()}Config")
    migrate.init_app(app, db)

    # 2) Initialiser les extensions
    # from .extensions import db, login_manager
    # db.init_app(app)
    # login_manager.init_app(app)
    # 3) Enregistrer les Blueprints
    from .views.main import bp_main
    app.register_blueprint(bp_main)
    return app