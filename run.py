# run.py
import os
from dotenv import load_dotenv

# Charge les variables du fichier .env
load_dotenv()

from app import create_app

app = create_app(os.getenv("FLASK_CONFIG"))

if __name__ == "__main__":
    app.run()