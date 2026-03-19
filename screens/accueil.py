"""
screens/accueil.py - Écran d'accueil CENAD
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
import os


class AccueilScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        with self.canvas.before:
            Color(0.07, 0.09, 0.30, 1)  # Bleu marine universitaire
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15),
                           size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # Logo/Header
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200),
                           spacing=dp(5))

        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.png')
        if os.path.exists(logo_path):
            logo = Image(source=logo_path, size_hint=(None, None), size=(dp(100), dp(100)),
                         pos_hint={'center_x': 0.5})
            header.add_widget(logo)
        else:
            # Placeholder cercle coloré
            from kivy.uix.widget import Widget
            header.add_widget(Widget(size_hint_y=None, height=dp(10)))

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
            text="Communauté des Étudiants\nNatifs d'Andapa à Antsiranana",
            font_size=dp(13),
            color=(0.7, 0.85, 1, 1),
            size_hint_y=None,
            height=dp(50),
            halign='center',
            text_size=(None, None)
        )
        tagline = Label(
            text="[i]Unis pour la réussite[/i]",
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

        # Séparateur
        sep = Label(text="─" * 40, color=(0.3, 0.4, 0.8, 0.6),
                    size_hint_y=None, height=dp(20))
        layout.add_widget(sep)

        # Boutons navigation
        nav_label = Label(text="[b]NAVIGATION[/b]", markup=True,
                          font_size=dp(12), color=(0.6, 0.7, 1, 1),
                          size_hint_y=None, height=dp(25))
        layout.add_widget(nav_label)

        buttons = [
            ("📊  Tableau de bord", "dashboard", "#1565C0"),
            ("🏢  Liste par bâtiment", "liste_batiment", "#1B5E20"),
            ("🎓  Liste par promotion", "liste_promotion", "#4A148C"),
            ("📜  Historique CENAD", "historique", "#BF360C"),
            ("🏛  Établissements", "etablissements", "#006064"),
            ("🔐  Administration", "admin", "#37474F"),
        ]

        for text, screen_name, color_hex in buttons:
            btn = NavButton(text=text, screen_name=screen_name,
                            bg_color=self._hex_to_rgba(color_hex))
            btn.bind(on_release=self.navigate)
            layout.add_widget(btn)

        # Footer
        footer = Label(
            text="© CENAD 2024 | Fondée en 2012",
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
            font_size=dp(14),
            halign='left',
            padding_x=dp(20),
            background_normal='',
            background_color=bg_color,
            color=(1, 1, 1, 1),
            **kwargs
        )
        self.screen_name = screen_name
