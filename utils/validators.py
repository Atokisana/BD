"""
utils/validators.py - Validation des données
"""
import re


def validate_email(email: str) -> bool:
    """Valide une adresse email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Valide un numéro de téléphone (format simple)"""
    # Accepte les formats avec espaces, tirets, etc.
    cleaned = re.sub(r'\D', '', phone)
    return len(cleaned) >= 7


def validate_name(name: str) -> bool:
    """Valide un nom (au moins 2 caractères)"""
    return len(name.strip()) >= 2


def validate_year(year: str) -> bool:
    """Valide une année (entre 2000 et 2100)"""
    try:
        y = int(year)
        return 2000 <= y <= 2100
    except:
        return False


def sanitize_text(text: str) -> str:
    """Nettoie un texte en supprimant les caractères spéciaux dangereux"""
    return text.replace("'", "''")
