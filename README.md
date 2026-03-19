# 📱 CENAD App
**Communauté des Étudiants Natifs d'Andapa à Antsiranana**

Application Android de gestion des membres développée en Python/Kivy.

---

## 🏗 Structure du projet

```
cenad_app/
├── main.py              # Point d'entrée de l'application
├── db_manager.py        # Gestion SQLite (CRUD + index + SHA-256)
├── analytics.py         # Statistiques Pandas/NumPy + graphiques Matplotlib
├── cenad.kv             # Styles globaux Kivy
├── buildozer.spec       # Configuration compilation APK
├── screens/
│   ├── accueil.py       # Écran d'accueil + navigation
│   ├── dashboard.py     # Recherche dynamique + statistiques + graphiques
│   ├── liste_batiment.py  # Membres groupés par bâtiment
│   ├── liste_promotion.py # Membres groupés par promotion
│   ├── historique.py    # Historique institutionnel CENAD
│   ├── etablissements.py  # Établissements universitaires d'Antsiranana
│   └── admin.py         # Administration CRUD sécurisée
├── data/
│   └── cenad.db         # Base SQLite (créée automatiquement)
└── assets/
    └── logo.png         # Logo CENAD (à ajouter)
```

---

## ⚡ Optimisations implémentées

### Base de données
- Index SQL sur `nom`, `promotion`, `batiment`, `niveau`
- Requêtes paramétrées (protection injection SQL)
- Chargement partiel : `SELECT id, nom, sexe... LIMIT 200`
- Pagination supportée

### Mémoire
- Lazy loading des écrans (`on_enter`)
- DataFrames Pandas créés uniquement pour l'analyse puis supprimés
- `plt.close('all')` après chaque graphique
- Images stockées en chemins, pas en binaire

### Interface
- Recherche avec debounce 400ms (évite requêtes excessives)
- Graphiques générés en arrière-plan (`threading`)
- RecycleView-compatible (BoxLayout avec `size_hint_y=None`)
- Transitions légères (`SlideTransition(duration=0.2)`)

### Android
- `on_pause()` retourne `True` (économie batterie)
- `plt.close('all')` dans `on_stop()`
- Backend Matplotlib : `Agg` (léger, compatible Android)

---

## 🔐 Sécurité

| Élément | Valeur |
|---------|--------|
| Mot de passe admin | `cenad2024` |
| Algorithme | SHA-256 |
| Changer le mot de passe | Modifier `ADMIN_PASSWORD_HASH` dans `db_manager.py` |

Pour générer un nouveau hash :
```python
import hashlib
print(hashlib.sha256("nouveau_mdp".encode()).hexdigest())
```

---

## 🚀 Lancement en développement

```bash
# Installer Kivy
pip install kivy pandas numpy matplotlib scipy

# Lancer l'application
cd cenad_app
python main.py
```

---

## 📦 Compilation APK avec Buildozer

### Prérequis (Ubuntu/Debian)
```bash
# Dépendances système
sudo apt update
sudo apt install -y python3-pip build-essential git \
    libssl-dev libffi-dev python3-dev \
    openjdk-17-jdk autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev

# Installer Buildozer
pip install buildozer cython==0.29.33

# Variables d'environnement Java
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

### Compilation
```bash
cd cenad_app

# Première compilation (debug, ~15-30 min)
buildozer android debug

# APK disponible ici :
# bin/cenad-1.0.0-armeabi-v7a-debug.apk

# Pour release
buildozer android release
```

### Déploiement direct (USB)
```bash
# Activer débogage USB sur le téléphone
buildozer android debug deploy run logcat
```

### Nettoyage
```bash
buildozer android clean
```

---

## 📊 Fonctionnalités par écran

| Écran | Fonctionnalités |
|-------|----------------|
| **Accueil** | Navigation, logo, infos CENAD |
| **Dashboard** | Recherche temps réel, filtres, stats, graphiques (barres, camembert) |
| **Bâtiment** | GROUP BY bâtiment, liste détaillée |
| **Promotion** | GROUP BY promotion, tri par année |
| **Historique** | Fondation 2012, présidents, mission |
| **Établissements** | 9 établissements avec mentions et parcours |
| **Admin** | Login SHA-256, CRUD complet (ajouter/modifier/supprimer) |

---

## 🗄 Schéma base de données

```sql
CREATE TABLE membres (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nom             TEXT NOT NULL,
    sexe            TEXT DEFAULT 'M',
    niveau          TEXT DEFAULT 'L1',  -- L1, L2, L3, M1, M2
    promotion       TEXT,
    batiment        TEXT,
    etablissement   TEXT,
    commune_origine TEXT,
    telephone       TEXT,
    photo           TEXT DEFAULT ''     -- Chemin fichier
);

CREATE INDEX idx_nom       ON membres(nom);
CREATE INDEX idx_promotion ON membres(promotion);
CREATE INDEX idx_batiment  ON membres(batiment);
CREATE INDEX idx_niveau    ON membres(niveau);
```

---

## 📤 Export données

Dans l'analytics, export CSV disponible :
```python
from analytics import export_csv
path = export_csv()  # Retourne le chemin du fichier CSV
```

---

## 🎨 Charte graphique

| Élément | Couleur |
|---------|---------|
| Fond principal | `#111B4E` (bleu marine) |
| Texte principal | Blanc / Bleu clair |
| Accent | `#FFD700` (or) |
| Bouton navigation | Bleu-violet variés |
| Admin | Vert (save), Rouge (delete) |

---

*© CENAD 2024 - Fondée en 2012 à Antsiranana, Madagascar*
