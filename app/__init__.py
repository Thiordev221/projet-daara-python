from flask import Flask
from .extension import db, migrate
from .models.classe import Classe
from .models.maitre import Maitre
from .models.progression import Progression
from .models.talibe import Talibe
from .views.classe import bp_classes
from .views.maitre import bp_maitres
from .views.progression import bp_progressions
from .views.talibe import bp_talibes


# from .models.classe import classe
# from .models.maitre import maitre
# from .models.progressiosn import prpogression
# from .models.talibe import talibes


def create_app(nom_config="dev"):
    app = Flask(__name__)
    app.config.from_object(
        f"config.{nom_config.capitalize()}Config")

    # 2) Initialiser les extensions
    # from .extensions import db, login_manager
    db.init_app(app)
    migrate.init_app(app, db)
    # login_manager.init_app(app)
    # 3) Enregistrer les Blueprints

    app.register_blueprint(bp_talibes)
    app.register_blueprint(bp_progressions)
    app.register_blueprint(bp_maitres)
    app.register_blueprint(bp_classes)
    return app