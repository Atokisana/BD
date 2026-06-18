"""
utils/helpers.py - Fonctions utilitaires
"""
from datetime import datetime
from pathlib import Path


def format_date(date_obj) -> str:
    """Formate une date en string lisible"""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%d/%m/%Y") if date_obj else ""


def get_file_size(filepath: str) -> str:
    """Retourne la taille d'un fichier en format lisible"""
    try:
        size_bytes = Path(filepath).stat().st_size
        for unit in ['B', 'KB', 'MB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} GB"
    except:
        return "?"


def ensure_directory(path: str):
    """Crée un répertoire s'il n'existe pas"""
    Path(path).mkdir(parents=True, exist_ok=True)


def safe_filename(filename: str) -> str:
    """Nettoie un nom de fichier"""
    import re
    return re.sub(r'[<>:"/\\|?*]', '', filename)
