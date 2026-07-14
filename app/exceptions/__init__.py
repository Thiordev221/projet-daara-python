# app/exceptions/__init__.py

class DaaraException(RuntimeError):
    """Classe de base pour toutes les exceptions de l'application Daara."""
    pass

# --- EXCEPTIONS MAÎTRE ---
class MaitreIntrouvableException(DaaraException):
    def __init__(self, matricule: str):
        super().__init__(f"Aucun maître trouvé pour le matricule : {matricule}")

class MaitreDejaExistantException(DaaraException):
    def __init__(self, matricule: str):
        super().__init__(f"Le maître avec le matricule {matricule} existe déjà.")

# --- EXCEPTIONS CLASSE ---
class ClasseIntrouvableException(DaaraException):
    def __init__(self, code: str):
        super().__init__(f"Aucune classe trouvée pour le code : {code}")

class ClasseDejaExistanteException(DaaraException):
    def __init__(self, code: str):
        super().__init__(f"La classe avec le code {code} existe déjà.")

# --- EXCEPTIONS TALIBÉ ---
class TalibeIntrouvableException(DaaraException):
    def __init__(self, matricule: str):
        super().__init__(f"Aucun talibé pour le matricule : {matricule}")

class TalibeDejaExistantException(DaaraException):
    def __init__(self, matricule: str):
        super().__init__(f"Le talibé avec le matricule {matricule} existe déjà.")

# --- EXCEPTIONS PROGRESSION ---
class ProgressionIntrouvableException(DaaraException):
    def __init__(self, id_progression: int):
        super().__init__(f"Aucun historique de progression trouvé pour l'ID : {id_progression}")

class ProgressionInvalideException(DaaraException):
    def __init__(self, message: str):
        super().__init__(f"Progression invalide : {message}")

# --- EXCEPTION GLOBALE DE SÉCURITÉ ---
class SuppressionImpossibleException(DaaraException):
    def __init__(self, message: str):
        super().__init__(f"Suppression impossible : {message}")