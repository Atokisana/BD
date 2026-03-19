"""
db_manager.py - Gestion optimisée de la base de données SQLite
CENAD - Communauté des Étudiants Natifs d'Andapa à Antsiranana
"""

import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'cenad.db')

# Mot de passe admin hashé en SHA-256 (par défaut: "cenad2024")
ADMIN_PASSWORD_HASH = hashlib.sha256("cenad2024".encode()).hexdigest()


def get_connection():
    """Retourne une connexion SQLite avec optimisations."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=1000")
    return conn


def init_db():
    """Initialise la base de données avec table et index."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            sexe TEXT DEFAULT 'M',
            niveau TEXT DEFAULT 'L1',
            promotion TEXT,
            batiment TEXT,
            etablissement TEXT,
            commune_origine TEXT,
            telephone TEXT,
            photo TEXT DEFAULT ''
        )
    ''')

    # Index pour recherches rapides
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nom ON membres(nom)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_promotion ON membres(promotion)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_batiment ON membres(batiment)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_niveau ON membres(niveau)")

    conn.commit()
    conn.close()


def insert_sample_data():
    """Insère des données d'exemple si la table est vide."""
    conn = get_connection()
    cursor = conn.cursor()
    count = cursor.execute("SELECT COUNT(*) FROM membres").fetchone()[0]
    if count > 0:
        conn.close()
        return

    sample = [
        ("RAKOTO Jean", "M", "L2", "2022", "BLOC A", "ENSET", "Andapa", "0341234567", ""),
        ("RABE Marie", "F", "L3", "2021", "BLOC B", "ESP", "Andapa", "0349876543", ""),
        ("ANDRIANTSOA Paul", "M", "M1", "2020", "PJ A", "SCIENCES", "Andapa", "0345678901", ""),
        ("RAZAFY Hanta", "F", "L1", "2023", "BLOC H", "FLSH", "Sambava", "0342345678", ""),
        ("RAMAROSON Eric", "M", "M2", "2019", "PJ B", "AGRO", "Andapa", "0343456789", ""),
        ("RAKOTOMALALA Lina", "F", "L2", "2022", "BLOC A", "ENSET", "Andapa", "0344567890", ""),
        ("ANDRIAMAMPIANINA Solo", "M", "L3", "2021", "BLOC C", "DEGSP", "Doany", "0345678902", ""),
        ("RAVOLAHY Prisca", "F", "L1", "2023", "PJ B", "ISAE", "Andapa", "0346789013", ""),
        ("RAJAONARISON Mamy", "M", "M1", "2020", "BLOC A", "IST", "Andapa", "0347890124", ""),
        ("RANDRIAMANANTENA Fara", "F", "L2", "2022", "PV C", "ISISFA", "Bealanana", "0348901235", ""),
        ("RABEMANANTSOA Nivo", "M", "L3", "2021", "Belle rose", "ENSET", "Andapa", "0340123456", ""),
        ("RAKOTONDRABE Vola", "F", "M2", "2019", "BLOC G", "ESP", "Andapa", "0341234568", ""),
        ("ANDRIANARY Henintsoa", "M", "L1", "2023", "PJ C", "SCIENCES", "Tsaratanana", "0342345679", ""),
        ("RAZANAJATOVO Tiana", "F", "L2", "2022", "PV B", "AGRO", "Andapa", "0343456790", ""),
        ("RAKOTOARIVO Fidy", "M", "M1", "2020", "BLOC I", "FLSH", "Andapa", "0344567891", ""),
    ]

    cursor.executemany(
        "INSERT INTO membres (nom, sexe, niveau, promotion, batiment, etablissement, commune_origine, telephone, photo) VALUES (?,?,?,?,?,?,?,?,?)",
        sample
    )
    conn.commit()
    conn.close()


# ===== CRUD Operations =====

def get_all_membres(limit=200, offset=0):
    """Charge les membres avec pagination."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, nom, sexe, niveau, promotion, batiment, etablissement FROM membres ORDER BY nom LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_membres(query="", niveau="", promotion="", batiment=""):
    """Recherche optimisée par SQL."""
    conn = get_connection()
    sql = "SELECT id, nom, sexe, niveau, promotion, batiment, etablissement FROM membres WHERE 1=1"
    params = []
    if query:
        sql += " AND nom LIKE ?"
        params.append(f"%{query}%")
    if niveau:
        sql += " AND niveau = ?"
        params.append(niveau)
    if promotion:
        sql += " AND promotion = ?"
        params.append(promotion)
    if batiment:
        sql += " AND batiment = ?"
        params.append(batiment)
    sql += " ORDER BY nom LIMIT 200"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_membre_by_id(membre_id):
    """Charge un membre complet par ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM membres WHERE id = ?", (membre_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_membre(data):
    """Ajoute un nouveau membre."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO membres (nom, sexe, niveau, promotion, batiment, etablissement, commune_origine, telephone, photo) VALUES (?,?,?,?,?,?,?,?,?)",
        (data['nom'], data['sexe'], data['niveau'], data['promotion'],
         data['batiment'], data['etablissement'], data['commune_origine'],
         data['telephone'], data.get('photo', ''))
    )
    conn.commit()
    conn.close()


def update_membre(membre_id, data):
    """Modifie un membre existant."""
    conn = get_connection()
    conn.execute(
        "UPDATE membres SET nom=?, sexe=?, niveau=?, promotion=?, batiment=?, etablissement=?, commune_origine=?, telephone=?, photo=? WHERE id=?",
        (data['nom'], data['sexe'], data['niveau'], data['promotion'],
         data['batiment'], data['etablissement'], data['commune_origine'],
         data['telephone'], data.get('photo', ''), membre_id)
    )
    conn.commit()
    conn.close()


def delete_membre(membre_id):
    """Supprime un membre."""
    conn = get_connection()
    conn.execute("DELETE FROM membres WHERE id = ?", (membre_id,))
    conn.commit()
    conn.close()


def get_stats_by_field(field):
    """Retourne statistiques groupées par champ (SQL direct, sans Pandas)."""
    allowed = ['niveau', 'promotion', 'batiment', 'sexe', 'etablissement']
    if field not in allowed:
        return {}
    conn = get_connection()
    rows = conn.execute(f"SELECT {field}, COUNT(*) as total FROM membres GROUP BY {field} ORDER BY total DESC").fetchall()
    conn.close()
    return {r[field]: r['total'] for r in rows}


def get_total_count():
    """Retourne le nombre total de membres."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM membres").fetchone()[0]
    conn.close()
    return count


def verify_admin_password(password):
    """Vérifie le mot de passe admin via SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH


def get_distinct_values(field):
    """Retourne les valeurs distinctes d'un champ pour les filtres."""
    allowed = ['niveau', 'promotion', 'batiment', 'etablissement']
    if field not in allowed:
        return []
    conn = get_connection()
    rows = conn.execute(f"SELECT DISTINCT {field} FROM membres WHERE {field} IS NOT NULL AND {field} != '' ORDER BY {field}").fetchall()
    conn.close()
    return [r[0] for r in rows]
