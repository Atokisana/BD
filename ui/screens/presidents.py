"""
ui/screens/presidents.py - Écran historique des présidents CENAD
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
import os
from config import IMAGES_DIR


class PresidentsScreen(Screen):
    """Écran d'affichage des présidents successifs"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._built = False

    def on_enter(self):
        """Construit l'UI à la première visite"""
        if not self._built:
            self.build_ui()
            self._built = True

    def build_ui(self):
        """Construit l'interface utilisateur"""
        # Fond
        with self.canvas.before:
            Color(*self.manager.app.theme['bg_primary'])
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg)

        main = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # ===== HEADER =====
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        back_btn = Button(
            text="◀",
            size_hint=(None, 1),
            width=dp(40),
            background_color=self.manager.app.theme['bg_secondary'],
            color=self.manager.app.theme['text_primary'],
            background_normal=''
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(back_btn)

        title = Label(
            text="[b]👑 PRÉSIDENTS[/b]",
            markup=True,
            font_size=dp(16),
            color=self.manager.app.theme['accent']
        )
        header.add_widget(title)

        main.add_widget(header)

        # ===== SUBTITLE =====
        subtitle = Label(
            text="Historique des leaders depuis 2012",
            font_size=dp(11),
            color=self.manager.app.theme['text_secondary'],
            size_hint_y=None,
            height=dp(22)
        )
        main.add_widget(subtitle)

        # ===== LISTE PRÉSIDENTS =====
        scroll = ScrollView()
        self.presidents_list = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            padding=(0, dp(5))
        )
        self.presidents_list.bind(minimum_height=self.presidents_list.setter('height'))

        # Données prédéfinies (à remplacer par DB si nécessaire)
        presidents_data = [
            {
                'nom': 'Richard',
                'prenom': 'JIMMY',
                'annee_debut': 2020,
                'annee_fin': 2022,
                'actions': 'Gestion de la période COVID-19, résilience associative',
                'photo': ''
            },
            {
                'nom': 'Fanios',
                'prenom': 'RALAHADY',
                'annee_debut': 2023,
                'annee_fin': 2024,
                'actions': 'Consolidation de l\'association',
                'photo': ''
            },
            {
                'nom': 'Flobert',
                'prenom': 'Mysco',
                'annee_debut': 2024,
                'annee_fin': 2025,
                'actions': 'Expansion et modernisation',
                'photo': ''
            },
            {
                'nom': 'Casmir',
                'prenom': 'BEVITA',
                'annee_debut': 2025,
                'annee_fin': 2026,
                'actions': 'Présidence actuelle',
                'photo': ''
            },
        ]

        for president in presidents_data:
            card = PresidentCard(president, self.manager.app.theme)
            self.presidents_list.add_widget(card)

        scroll.add_widget(self.presidents_list)
        main.add_widget(scroll)

        self.add_widget(main)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos


class PresidentCard(BoxLayout):
    """Carte de présentation d'un président"""

    def __init__(self, president: dict, theme: dict, **kwargs):
        super().__init__(
            orientation='vertical',
            size_hint_y=None,
            height=dp(140),
            padding=dp(10),
            spacing=dp(5),
            **kwargs
        )
        self.president = president
        self.theme = theme

        # Fond coloré
        with self.canvas.before:
            Color(*theme['bg_secondary'])
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.rect, 'size', self.size),
                  pos=lambda *a: setattr(self.rect, 'pos', self.pos))

        # En-tête avec nom et années
        header_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))

        nom_complet = f"{president.get('prenom', '')} {president.get('nom', '')}".strip()
        header_box.add_widget(Label(
            text=f"[b]{nom_complet}[/b]",
            markup=True,
            font_size=dp(13),
            bold=True,
            color=theme['accent'],
            halign='left',
            text_size=(None, None),
            size_hint=(0.6, 1)
        ))

        period = f"{president.get('annee_debut', '')} – {president.get('annee_fin', '')}"
        header_box.add_widget(Label(
            text=period,
            font_size=dp(11),
            color=theme['text_secondary'],
            halign='right',
            size_hint=(0.4, 1)
        ))

        self.add_widget(header_box)

        # Actions marquantes
        actions = president.get('actions', 'Pas d\'informations')
        actions_label = Label(
            text=f"[i]{actions}[/i]",
            markup=True,
            font_size=dp(10),
            color=theme['text_primary'],
            halign='left',
            text_size=(None, None),
            size_hint_y=None
        )
        actions_label.bind(
            width=lambda *x: setattr(actions_label, 'text_size', (actions_label.width, None)),
            texture_size=lambda *x: setattr(actions_label, 'height', actions_label.texture_size[1])
        )
        self.add_widget(actions_label)

        # Bouton détail
        detail_btn = Button(
            text="Voir détail",
            size_hint_y=None,
            height=dp(35),
            background_color=theme['accent'],
            color=theme['bg_primary'],
            background_normal=''
        )
        detail_btn.bind(on_release=lambda x: self._show_detail())
        self.add_widget(detail_btn)

    def _show_detail(self):
        """Affiche un popup avec détails"""
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        nom_complet = f"{self.president.get('prenom', '')} {self.president.get('nom', '')}".strip()

        content.add_widget(Label(
            text=f"[b]{nom_complet}[/b]",
            markup=True,
            font_size=dp(16),
            color=self.theme['accent'],
            size_hint_y=None,
            height=dp(40)
        ))

        period = f"{self.president.get('annee_debut', '')} – {self.president.get('annee_fin', '')}"
        content.add_widget(Label(
            text=f"Mandat : {period}",
            font_size=dp(12),
            color=self.theme['text_secondary'],
            size_hint_y=None,
            height=dp(30)
        ))

        content.add_widget(Label(
            text="Actions marquantes",
            font_size=dp(11),
            bold=True,
            color=self.theme['accent'],
            size_hint_y=None,
            height=dp(25)
        ))

        actions = self.president.get('actions', 'Pas d\'informations')
        actions_label = Label(
            text=actions,
            font_size=dp(11),
            color=self.theme['text_primary'],
            halign='left',
            text_size=(None, None),
            size_hint_y=None
        )
        actions_label.bind(
            width=lambda *x: setattr(actions_label, 'text_size', (actions_label.width, None)),
            texture_size=lambda *x: setattr(actions_label, 'height', actions_label.texture_size[1])
        )
        content.add_widget(actions_label)

        close_btn = Button(
            text="Fermer",
            size_hint_y=None,
            height=dp(44),
            background_color=self.theme['bg_secondary'],
            color=self.theme['text_primary'],
            background_normal=''
        )

        popup = Popup(
            title=nom_complet,
            content=content,
            size_hint=(0.9, 0.6),
            background_color=self.theme['bg_primary']
        )

        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        popup.open()
