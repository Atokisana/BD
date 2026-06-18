"""
config.py - Configuration centralisée de l'application CENAD
"""
import os
from enum import Enum

# ===== CHEMINS =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
ICONS_DIR = os.path.join(ASSETS_DIR, 'icons')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
LOGOS_DIR = os.path.join(ASSETS_DIR, 'logos')

# Créer les répertoires s'ils n'existent pas
for dir_path in [DATA_DIR, ASSETS_DIR, ICONS_DIR, IMAGES_DIR, LOGOS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, 'cenad.db')

# ===== SÉCURITÉ =====
import hashlib
ADMIN_PASSWORD_HASH = hashlib.sha256("cenad2024".encode()).hexdigest()

# ===== THÈMES =====
class Theme(Enum):
    DARK = "dark"
    LIGHT = "light"

COLORS_DARK = {
    'bg_primary': (0.07, 0.09, 0.30, 1),      # Bleu marine
    'bg_secondary': (0.05, 0.07, 0.22, 1),
    'text_primary': (1, 1, 1, 1),
    'text_secondary': (0.6, 0.8, 1, 0.8),
    'accent': (1, 0.85, 0.1, 1),              # Or
    'error': (1, 0.3, 0.3, 1),
    'success': (0.13, 0.55, 0.13, 1),
    'warning': (1, 0.85, 0.1, 1),
}

COLORS_LIGHT = {
    'bg_primary': (0.95, 0.96, 0.98, 1),
    'bg_secondary': (0.88, 0.90, 0.95, 1),
    'text_primary': (0.1, 0.1, 0.1, 1),
    'text_secondary': (0.4, 0.4, 0.5, 1),
    'accent': (0.15, 0.65, 0.15, 1),
    'error': (0.8, 0.1, 0.1, 1),
    'success': (0.2, 0.7, 0.2, 1),
    'warning': (1, 0.65, 0.0, 1),
}

# ===== INFO APP =====
APP_NAME = "CENAD"
APP_VERSION = "1.0.0"
APP_AUTHOR = "CENAD Association"
APP_DESCRIPTION = "Communauté des Étudiants Natifs d'Andapa à Antsiranana"
FOUNDED_YEAR = 2012

# ===== COMMUNES D'ANDAPA =====
COMMUNES_ANDAPA = [
    "Andapa",
    "Sambava",
    "Doany",
    "Bealanana",
    "Tsaratanana",
    "Vohémar",
    "Antalaha",
    "Maroantsetra",
    "Maromandia",
    "Mananara-Nord",
    "Soanierana-Ivongo",
    "Sambava",
    "Vohemar",
    "Andapa",
]

# ===== ÉTABLISSEMENTS =====
ESTABLISHMENTS = [
    {
        'nom': 'ENSET',
        'complet': 'École Normale Supérieure pour l\'Enseignement Technique',
        'mission': 'Former des enseignants techniques et des ingénieurs pédagogiques',
        'filieres': ['Génie Civil', 'Génie Électrique', 'Génie Informatique', 'Génie Mécanique'],
        'color': '#1565C0'
    },
    {
        'nom': 'ESP',
        'complet': 'École Supérieure Polytechnique',
        'mission': 'Former des ingénieurs polytechniciens spécialisés',
        'filieres': ['Génie Civil', 'Génie Électrique', 'Génie Informatique'],
        'color': '#4527A0'
    },
    {
        'nom': 'AGRO',
        'complet': 'École Supérieure des Sciences Agronomiques',
        'mission': 'Former des agronomes et spécialistes du développement rural',
        'filieres': ['Agronomie', 'Zootechnie', 'Foresterie', 'Aquaculture'],
        'color': '#2E7D32'
    },
    {
        'nom': 'SCIENCES',
        'complet': 'Faculté des Sciences',
        'mission': 'Enseignement des sciences fondamentales et appliquées',
        'filieres': ['Mathématiques', 'Physique', 'Chimie', 'Biologie', 'Informatique'],
        'color': '#00695C'
    },
    {
        'nom': 'FLSH',
        'complet': 'Faculté des Lettres et Sciences Humaines',
        'mission': 'Formation en lettres, langues, sciences sociales et humaines',
        'filieres': ['Lettres Modernes', 'Histoire-Géographie', 'Anglais', 'Sociologie'],
        'color': '#BF360C'
    },
    {
        'nom': 'DEGSP',
        'complet': 'Droit, Économie, Gestion et Science Politique',
        'mission': 'Former des juristes, économistes, gestionnaires et politologues',
        'filieres': ['Droit', 'Économie', 'Gestion', 'Finance', 'Sciences Politiques'],
        'color': '#F57F17'
    },
    {
        'nom': 'ISAE',
        'complet': 'Institut Supérieur d\'Administration et d\'Entreprise',
        'mission': 'Former des cadres en administration et gestion d\'entreprise',
        'filieres': ['Administration', 'Gestion', 'Management', 'Commerce'],
        'color': '#6A1B9A'
    },
    {
        'nom': 'IST',
        'complet': 'Institut Supérieur de Technologie',
        'mission': 'Formation professionnelle en technologies appliquées',
        'filieres': ['Informatique', 'Réseaux', 'Maintenance industrielle', 'Électronique'],
        'color': '#006064'
    },
    {
        'nom': 'ISISFA',
        'complet': 'Institut Supérieur de l\'Infirmier et Sage-Femme',
        'mission': 'Former des infirmiers et sages-femmes qualifiés',
        'filieres': ['Soins Infirmiers', 'Sage-Femme', 'Santé Publique'],
        'color': '#1565C0'
    },
]

# ===== NIVEAUX D'ÉTUDE =====
STUDY_LEVELS = ["L1", "L2", "L3", "M1", "M2"]

# ===== BÂTIMENTS (PAR DÉFAUT) =====
DEFAULT_BUILDINGS = [
    "BLOC A", "BLOC B", "BLOC C", "BLOC D", "BLOC E",
    "BLOC F", "BLOC G", "BLOC H", "BLOC I", "BLOC J",
    "PJ A", "PJ B", "PJ C",
    "Belle Rose",
    "PV B", "PV C",
]
