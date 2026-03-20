"""
screens/accueil.py - Écran d'accueil CENAD
Corrections : chemin logo Android, remplacement emojis par texte/formes
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import platform
import os


def get_asset_path(filename):
    """Retourne le bon chemin selon la plateforme."""
    if platform == 'android':
        from android.storage import app_storage_path
        # Sur Android, les assets sont dans le dossier de l'app
        base = os.path.dirname(os.path.abspath(__file__))
        # Remonter d'un niveau pour trouver assets/
        root = os.path.dirname(base)
        path = os.path.join(root, 'assets', filename)
        if os.path.exists(path):
            return path
        # Essai alternatif
        path2 = os.path.join(base, '..', 'assets', filename)
        return path2
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, 'assets', filename)


class AccueilScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        with self.canvas.before:
            Color(0.07, 0.09, 0.30, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15),
                           size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # Logo
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200),
                           spacing=dp(5))

        # CORRECTION : chercher logo.PNG (majuscule) et logo.png
        logo_found = False
        for fname in ['logo.PNG', 'logo.png']:
            logo_path = get_asset_path(fname)
            if os.path.exists(logo_path):
                logo = Image(source=logo_path, size_hint=(None, None),
                             size=(dp(100), dp(100)),
                             pos_hint={'center_x': 0.5})
                header.add_widget(logo)
                logo_found = True
                break

        if not logo_found:
            # Placeholder cercle doré si pas de logo
            from kivy.uix.widget import Widget
            placeholder = Widget(size_hint=(None, None), size=(dp(80), dp(80)),
                                 pos_hint={'center_x': 0.5})
            with placeholder.canvas:
                Color(1, 0.85, 0.1, 1)
                from kivy.graphics import Ellipse
                placeholder._ellipse = Ellipse(
                    size=(dp(80), dp(80)), pos=placeholder.pos)
                placeholder.bind(pos=lambda w, p: setattr(w._ellipse, 'pos', p))
            header.add_widget(placeholder)

        title = Label(
            text="[b]CENAD[/b]",
            markup=True,
            font_size=dp(28),
            color=(1, 0.85, 0.1, 1),
            size_hint_y=None,
            height=dp(45),
            halign='center'
        )
        subtitle = Label(
            text="Communaute des Etudiants\nNatifs d'Andapa a Antsiranana",
            font_size=dp(13),
            color=(0.7, 0.85, 1, 1),
            size_hint_y=None,
            height=dp(50),
            halign='center',
        )
        tagline = Label(
            text="[i]Unis pour la reussite[/i]",
            markup=True,
            font_size=dp(11),
            color=(0.5, 0.8, 0.5, 1),
            size_hint_y=None,
            height=dp(25),
            halign='center'
        )
        header.add_widget(title)
        header.add_widget(subtitle)
        header.add_widget(tagline)
        layout.add_widget(header)

        sep = Label(text="", size_hint_y=None, height=dp(5))
        layout.add_widget(sep)

        nav_label = Label(text="[b]NAVIGATION[/b]", markup=True,
                          font_size=dp(12), color=(0.6, 0.7, 1, 1),
                          size_hint_y=None, height=dp(25))
        layout.add_widget(nav_label)

        # CORRECTION : texte sans emojis (incompatibles Android par defaut)
        buttons = [
            ("[Dashboard]  Tableau de bord", "dashboard", "#1565C0"),
            ("[Batiment]   Liste par batiment", "liste_batiment", "#1B5E20"),
            ("[Promo]      Liste par promotion", "liste_promotion", "#4A148C"),
            ("[Historique] Historique CENAD", "historique", "#BF360C"),
            ("[Campus]     Etablissements", "etablissements", "#006064"),
            ("[Admin]      Administration", "admin", "#37474F"),
        ]

        for text, screen_name, color_hex in buttons:
            btn = NavButton(text=text, screen_name=screen_name,
                            bg_color=self._hex_to_rgba(color_hex))
            btn.bind(on_release=self.navigate)
            layout.add_widget(btn)

        footer = Label(
            text="(c) CENAD 2024 | Fondee en 2012",
            font_size=dp(10),
            color=(0.4, 0.5, 0.7, 0.8),
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(footer)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    def navigate(self, btn):
        self.manager.current = btn.screen_name

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def _hex_to_rgba(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))
        return (r, g, b, 1)


class NavButton(Button):
    def __init__(self, text, screen_name, bg_color=(0.1, 0.3, 0.8, 1), **kwargs):
        super().__init__(
            text=text,
            size_hint_y=None,
            height=dp(52),
            font_size=dp(13),
            halign='left',
            padding_x=dp(20),
            background_normal='',
            background_color=bg_color,
            color=(1, 1, 1, 1),
            **kwargs
        )
        self.screen_name = screen_name
