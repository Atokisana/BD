# CENAD App v2.0
**Communaute des Etudiants Natifs d'Andapa a Antsiranana**

Application Android de gestion des membres developpee en Python/Kivy.

---

## Structure du projet

```
cenad_app/
├── main.py                # Point d'entree de l'application
├── db_manager.py          # Gestion SQLite (CRUD + index + SHA-256)
├── analytics.py           # Statistiques Pandas/NumPy + graphiques Matplotlib
├── toast.py               # Systeme de notifications toast
├── cenad.kv               # Styles globaux Kivy (boutons arrondis, cartes)
├── buildozer.spec         # Configuration compilation APK (arm + arm64)
├── screens/
│   ├── accueil.py         # Ecran d'accueil + menu lateral + navigation
│   ├── dashboard.py       # Recherche avancee (3 filtres) + statistiques + graphiques
│   ├── detail_membre.py   # Profil complet d'un membre (nouveau)
│   ├── liste_batiment.py  # Membres groupes par batiment
│   ├── liste_promotion.py # Membres groupes par promotion
│   ├── historique.py      # Historique institutionnel CENAD
│   ├── etablissements.py  # Etablissements universitaires d'Antsiranana
│   └── admin.py           # Administration CRUD securisee (avec recherche)
├── data/
│   └── cenad.db           # Base SQLite (creee automatiquement)
└── assets/
    ├── cenad_icon.png     # Icone application
    ├── logo.PNG           # Logo CENAD
    └── icons/             # Icones de navigation
```

---

## Nouveautes v2.0

### Ecran de detail membre
- Tap sur un membre dans le Dashboard pour voir son profil complet
- Avatar avec initiales et couleur selon le sexe
- Toutes les informations affichees dans des cartes colorees
- Bouton retour Android supporte

### Dashboard ameliore
- **3 filtres** : Niveau + Batiment + Promotion (valeurs dynamiques depuis la DB)
- Compteur de resultats en temps reel
- Graphique camembert pour la repartition par sexe
- Tap sur un membre pour voir son detail

### Administration amelioree
- **Recherche** dans la liste des membres
- Compteur de membres affiche
- Champ batiment libre (plus de liste fixe)
- Validation des donnees (nom obligatoire, telephone valide)
- **Notifications toast** pour les confirmations (ajout, modification, suppression)

### Ameliorations visuelles
- Boutons arrondis globalement (radius 8dp)
- Inputs avec coins arrondis
- Spinners avec design moderne
- Cartes avec RoundedRectangle et accents colores
- Touch feedback sur les lignes de membres

### Configuration
- Support arm64-v8a (en plus de armeabi-v7a)
- API Android 34
- Fichier .gitignore corrige (renomme depuis gitignore)
- Charts generes exclus du git
- source.exclude_dirs pour __pycache__ et .git

---

## Optimisations

### Base de donnees
- Index SQL sur `nom`, `promotion`, `batiment`, `niveau`
- Requetes parametrees (protection injection SQL)
- Chargement partiel : `SELECT ... LIMIT 200`
- Pagination supportee

### Memoire
- Lazy loading des ecrans (`on_enter`)
- DataFrames Pandas crees uniquement pour l'analyse puis supprimes
- `plt.close('all')` apres chaque graphique
- Images stockees en chemins, pas en binaire

### Interface
- Recherche avec debounce 400ms (evite requetes excessives)
- Graphiques generes en arriere-plan (`threading`)
- Transitions legeres (`SlideTransition(duration=0.2)`)
- Notifications toast non-bloquantes

### Android
- `on_pause()` retourne `True` (economie batterie)
- `plt.close('all')` dans `on_stop()`
- Backend Matplotlib : `Agg` (leger, compatible Android)
- Bouton retour intercepte correctement sur tous les ecrans

---

## Securite

| Element | Valeur |
|---------|--------|
| Mot de passe admin | `cenad2024` |
| Algorithme | SHA-256 |
| Changer le mot de passe | Modifier `ADMIN_PASSWORD_HASH` dans `db_manager.py` |

Pour generer un nouveau hash :
```python
import hashlib
print(hashlib.sha256("nouveau_mdp".encode()).hexdigest())
```

---

## Lancement en developpement

```bash
# Installer les dependances
pip install kivy pandas numpy matplotlib scipy

# Lancer l'application
python main.py
```

---

## Compilation APK avec Buildozer

### Prerequis (Ubuntu/Debian)
```bash
# Dependances systeme
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
# Premiere compilation (debug, ~15-30 min)
buildozer android debug

# APK disponible ici :
# bin/cenad-2.0.0-armeabi-v7a-debug.apk
# bin/cenad-2.0.0-arm64-v8a-debug.apk

# Pour release
buildozer android release
```

### Deploiement direct (USB)
```bash
# Activer debogage USB sur le telephone
buildozer android debug deploy run logcat
```

---

## Fonctionnalites par ecran

| Ecran | Fonctionnalites |
|-------|----------------|
| **Accueil** | Navigation, logo, menu lateral, infos CENAD |
| **Dashboard** | Recherche temps reel, 3 filtres, stats, graphiques (barres + camembert) |
| **Detail Membre** | Profil complet, avatar, cartes d'info colorees |
| **Batiment** | GROUP BY batiment, liste detaillee |
| **Promotion** | GROUP BY promotion, tri par annee |
| **Historique** | Fondation 2012, presidents, mission |
| **Etablissements** | 9 etablissements avec mentions et parcours |
| **Admin** | Login SHA-256, recherche, CRUD complet, validation, toast |

---

## Schema base de donnees

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

## Charte graphique

| Element | Couleur |
|---------|---------|
| Fond principal | `#0D1340` (bleu marine) |
| Texte principal | Blanc / Bleu clair |
| Accent | `#FFD700` (or) |
| Bouton navigation | Bleu-violet varies |
| Admin | Vert (save), Rouge (delete) |
| Toast succes | Vert semi-transparent |
| Toast erreur | Rouge semi-transparent |

---

## Export donnees

```python
from analytics import export_csv
path = export_csv()  # Retourne le chemin du fichier CSV
```

---

**(c) CENAD 2024-2025 | Fondee en 2012 a Antsiranana, Madagascar**
