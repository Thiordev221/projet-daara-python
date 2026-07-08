# config.py
import os
class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "cle_secrete_ultra_securisee_pour_la_daara")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
    "DEV_DATABASE_URL",
    "postgresql+psycopg2://postgres:Thior552005@localhost:5432/daara_dev"
    )

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://monblog_user:monMotDePasse@localhost:5432/monblog_test"
    )
class ProdConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DATABASE_URL", "postgresql+psycopg2://admin_prod:Thior552005_robuste@serveur_distant:5432/daara_prod")