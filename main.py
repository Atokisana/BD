"""
main.py - Point d'entrée principal de l'application CENAD
Corrections : bouton retour Android, clavier persistant, emojis
"""
import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

os.environ['KIVY_NO_ENV_CONFIG'] = '1'

from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '0')
# CORRECTION : clavier Android persistant
Config.set('kivy', 'keyboard_mode', 'systemanddock')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.core.text import LabelBase
import db_manager as db


class CENADApp(App):
    title = "CENAD"

    def build(self):
        Window.clearcolor = (0.07, 0.09, 0.30, 1)

        # CORRECTION : bouton retour Android
        Window.bind(on_keyboard=self._on_keyboard)

        db.init_db()
        db.insert_sample_data()

        sm = ScreenManager(transition=SlideTransition(duration=0.2))

        from screens.accueil import AccueilScreen
        from screens.dashboard import DashboardScreen
        from screens.liste_batiment import ListeBatimentScreen
        from screens.liste_promotion import ListePromotionScreen
        from screens.historique import HistoriqueScreen
        from screens.etablissements import EtablissementsScreen
        from screens.admin import AdminScreen

        sm.add_widget(AccueilScreen(name='accueil'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(ListeBatimentScreen(name='liste_batiment'))
        sm.add_widget(ListePromotionScreen(name='liste_promotion'))
        sm.add_widget(HistoriqueScreen(name='historique'))
        sm.add_widget(EtablissementsScreen(name='etablissements'))
        sm.add_widget(AdminScreen(name='admin'))

        sm.current = 'accueil'
        self.sm = sm
        return sm

    def _on_keyboard(self, window, key, *args):
        """CORRECTION : intercepte le bouton retour Android (keycode 27)."""
        if key == 27:  # Bouton retour Android
            current = self.sm.current
            if current == 'accueil':
                return False  # Quitte l'app
            else:
                self.sm.current = 'accueil'
                return True  # Consomme l'événement, ne quitte pas
        return False

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except Exception:
            pass


if __name__ == '__main__':
    CENADApp().run()
