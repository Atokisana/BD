"""
main.py - Point d'entrée principal de l'application CENAD
Communauté des Étudiants Natifs d'Andapa à Antsiranana

Architecture MVC modulaire optimisée pour Android
"""

import os
import sys

# Chemin du projet
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

# Configuration Kivy AVANT tout import kivy
os.environ['KIVY_NO_ENV_CONFIG'] = '1'

from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '0')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition, NoTransition
from kivy.core.window import Window
from kivy.clock import Clock

import db_manager as db


class CENADApp(App):
    title = "CENAD"

    def build(self):
        # Couleur de fond globale
        Window.clearcolor = (0.07, 0.09, 0.30, 1)

        # Initialisation base de données
        db.init_db()
        db.insert_sample_data()

        # Gestionnaire d'écrans avec transition légère
        sm = ScreenManager(transition=SlideTransition(duration=0.2))

        # Import différé des screens pour lazy loading
        from screens.accueil import AccueilScreen
        from screens.dashboard import DashboardScreen
        from screens.liste_batiment import ListeBatimentScreen
        from screens.liste_promotion import ListePromotionScreen
        from screens.historique import HistoriqueScreen
        from screens.etablissements import EtablissementsScreen
        from screens.admin import AdminScreen

        # Ajout des écrans
        sm.add_widget(AccueilScreen(name='accueil'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(ListeBatimentScreen(name='liste_batiment'))
        sm.add_widget(ListePromotionScreen(name='liste_promotion'))
        sm.add_widget(HistoriqueScreen(name='historique'))
        sm.add_widget(EtablissementsScreen(name='etablissements'))
        sm.add_widget(AdminScreen(name='admin'))

        sm.current = 'accueil'
        return sm

    def on_pause(self):
        """Gestion pause Android (économie batterie)."""
        return True

    def on_resume(self):
        """Reprise après pause."""
        pass

    def on_stop(self):
        """Nettoyage à la fermeture."""
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except Exception:
            pass


if __name__ == '__main__':
    CENADApp().run()
