"""
Modèles de données avec validation
"""
from datetime import datetime
from typing import Optional

class Membre:
    """Modèle d'un membre CENAD"""
    def __init__(self, id: int = None, nom: str = "", prenom: str = "",
                 sexe: str = "M", niveau: str = "L1", promotion: str = "",
                 etablissement: str = "", batiment: str = "",
                 commune_origine: str = "", telephone: str = "",
                 photo_filename: str = ""):
        self.id = id
        self.nom = nom.strip()
        self.prenom = prenom.strip()
        self.sexe = sexe
        self.niveau = niveau
        self.promotion = promotion
        self.etablissement = etablissement
        self.batiment = batiment
        self.commune_origine = commune_origine
        self.telephone = telephone
        self.photo_filename = photo_filename

    def nom_complet(self) -> str:
        return f"{self.prenom} {self.nom}".strip()

    def to_dict(self) -> dict:
        return {
            'id': self.id, 'nom': self.nom, 'prenom': self.prenom,
            'sexe': self.sexe, 'niveau': self.niveau, 'promotion': self.promotion,
            'etablissement': self.etablissement, 'batiment': self.batiment,
            'commune_origine': self.commune_origine, 'telephone': self.telephone,
            'photo_filename': self.photo_filename
        }


class President:
    """Modèle d'un président CENAD"""
    def __init__(self, id: int = None, nom: str = "", prenom: str = "",
                 annee_debut: int = 2012, annee_fin: int = 2013,
                 photo_filename: str = "", actions_marquantes: str = ""):
        self.id = id
        self.nom = nom.strip()
        self.prenom = prenom.strip()
        self.annee_debut = annee_debut
        self.annee_fin = annee_fin
        self.photo_filename = photo_filename
        self.actions_marquantes = actions_marquantes

    def nom_complet(self) -> str:
        return f"{self.prenom} {self.nom}".strip()

    def periode(self) -> str:
        return f"{self.annee_debut} – {self.annee_fin}"

    def to_dict(self) -> dict:
        return {
            'id': self.id, 'nom': self.nom, 'prenom': self.prenom,
            'annee_debut': self.annee_debut, 'annee_fin': self.annee_fin,
            'photo_filename': self.photo_filename, 'actions_marquantes': self.actions_marquantes
        }


class Batiment:
    """Modèle d'un bâtiment"""
    def __init__(self, id: int = None, nom: str = "", description: str = ""):
        self.id = id
        self.nom = nom.strip()
        self.description = description.strip()

    def to_dict(self) -> dict:
        return {'id': self.id, 'nom': self.nom, 'description': self.description}


class Etablissement:
    """Modèle d'un établissement universitaire"""
    def __init__(self, id: int = None, nom: str = "", mission: str = "",
                 filieres: list = None):
        self.id = id
        self.nom = nom.strip()
        self.mission = mission.strip()
        self.filieres = filieres or []

    def to_dict(self) -> dict:
        return {'id': self.id, 'nom': self.nom, 'mission': self.mission,
                'filieres': self.filieres}
