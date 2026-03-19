"""
analytics.py - Analyse statistique avec Pandas/NumPy
CENAD - Communauté des Étudiants Natifs d'Andapa à Antsiranana
"""

import io
import os

# Imports conditionnels pour Android
try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import matplotlib
    matplotlib.use('Agg')  # Backend léger compatible Android
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from db_manager import get_connection


def get_dataframe():
    """Charge les données dans un DataFrame Pandas (uniquement quand nécessaire)."""
    if not HAS_PANDAS:
        return None
    conn = get_connection()
    df = pd.read_sql_query("SELECT niveau, promotion, batiment, sexe, etablissement FROM membres", conn)
    conn.close()
    return df


def compute_stats():
    """Calcule toutes les statistiques descriptives."""
    conn = get_connection()
    stats = {}

    # Total
    stats['total'] = conn.execute("SELECT COUNT(*) FROM membres").fetchone()[0]

    # Par sexe
    rows = conn.execute("SELECT sexe, COUNT(*) FROM membres GROUP BY sexe").fetchall()
    stats['par_sexe'] = {r[0]: r[1] for r in rows}

    # Par niveau
    rows = conn.execute("SELECT niveau, COUNT(*) FROM membres GROUP BY niveau ORDER BY niveau").fetchall()
    stats['par_niveau'] = {r[0]: r[1] for r in rows}

    # Par bâtiment
    rows = conn.execute("SELECT batiment, COUNT(*) FROM membres GROUP BY batiment ORDER BY batiment").fetchall()
    stats['par_batiment'] = {r[0]: r[1] for r in rows}

    # Par promotion
    rows = conn.execute("SELECT promotion, COUNT(*) FROM membres GROUP BY promotion ORDER BY promotion DESC").fetchall()
    stats['par_promotion'] = {r[0]: r[1] for r in rows}

    # Par établissement
    rows = conn.execute("SELECT etablissement, COUNT(*) FROM membres GROUP BY etablissement ORDER BY COUNT(*) DESC").fetchall()
    stats['par_etablissement'] = {r[0]: r[1] for r in rows}

    conn.close()

    # Analyses NumPy si disponible
    if HAS_PANDAS and stats['total'] > 0:
        values = list(stats['par_niveau'].values())
        if values:
            stats['niveau_mean'] = float(np.mean(values))
            stats['niveau_std'] = float(np.std(values))
            stats['niveau_max'] = int(np.max(values))

    return stats


def generate_bar_chart(data_dict, title, xlabel, ylabel, color='#1E88E5'):
    """
    Génère un graphique en barres et retourne le chemin du fichier image.
    Ferme la figure après usage pour libérer la mémoire.
    """
    if not HAS_MATPLOTLIB or not data_dict:
        return None

    fig, ax = plt.subplots(figsize=(6, 4), facecolor='#1A237E')
    ax.set_facecolor('#0D1B4B')

    labels = list(data_dict.keys())
    values = list(data_dict.values())

    bars = ax.bar(labels, values, color=color, alpha=0.85, edgecolor='white', linewidth=0.5)

    # Labels sur les barres
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                str(val), ha='center', va='bottom', color='white', fontsize=9, fontweight='bold')

    ax.set_title(title, color='white', fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel(xlabel, color='#90CAF9', fontsize=9)
    ax.set_ylabel(ylabel, color='#90CAF9', fontsize=9)
    ax.tick_params(colors='white', labelsize=8)
    ax.spines['bottom'].set_color('#3949AB')
    ax.spines['left'].set_color('#3949AB')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()

    # Sauvegarde temporaire
    path = os.path.join(os.path.dirname(__file__), 'data', f'chart_{title[:10].replace(" ","_")}.png')
    fig.savefig(path, dpi=100, bbox_inches='tight', facecolor='#1A237E')
    plt.close('all')  # Libérer mémoire

    return path


def generate_pie_chart(data_dict, title):
    """Génère un diagramme en camembert."""
    if not HAS_MATPLOTLIB or not data_dict:
        return None

    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#1A237E')

    labels = list(data_dict.keys())
    values = list(data_dict.values())
    colors = ['#1E88E5', '#E91E63', '#43A047', '#FB8C00', '#8E24AA',
              '#00ACC1', '#F4511E', '#6D4C41', '#039BE5', '#7CB342']

    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct='%1.1f%%',
        colors=colors[:len(labels)], startangle=90,
        textprops={'color': 'white', 'fontsize': 8},
        wedgeprops={'edgecolor': '#1A237E', 'linewidth': 1.5}
    )
    for at in autotexts:
        at.set_fontsize(7)
        at.set_color('white')

    ax.set_title(title, color='white', fontsize=11, fontweight='bold', pad=10)
    plt.tight_layout()

    path = os.path.join(os.path.dirname(__file__), 'data', f'pie_{title[:10].replace(" ","_")}.png')
    fig.savefig(path, dpi=100, bbox_inches='tight', facecolor='#1A237E')
    plt.close('all')

    return path


def export_csv():
    """Exporte tous les membres en CSV."""
    if not HAS_PANDAS:
        return None
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM membres", conn)
    conn.close()
    path = os.path.join(os.path.dirname(__file__), 'data', 'export_membres.csv')
    df.to_csv(path, index=False, encoding='utf-8-sig')
    del df
    return path
