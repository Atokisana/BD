"""
screens/historique.py - Historique institutionnel de la CENAD
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp


PRESIDENTS = [
    ("RAKOTO Andriamanana", "2012 – 2013", "Fondateur et premier président. Mise en place des statuts."),
    ("RABE Tahina", "2013 – 2014", "Développement du réseau d'entraide entre membres."),
    ("ANDRIAMAMPIANINA Solo", "2014 – 2015", "Organisation des premières activités socioculturelles."),
    ("RAZAFY Narindra", "2015 – 2016", "Renforcement des partenariats avec les établissements."),
    ("RAKOTONDRABE Fidy", "2016 – 2018", "Expansion du nombre de membres et digitalisation."),
    ("RANDRIAMANANTENA Vola", "2018 – 2020", "Lancement des activités sportives et académiques."),
    ("ANDRIANTSOA Jean", "2020 – 2022", "Gestion de la période COVID-19, résilience associative."),
    ("RAKOTOMALALA Henintsoa", "2022 – présent", "Modernisation et vision stratégique 2024–2026."),
]

HISTORIQUE_TEXT = """
La CENAD (Communauté des Étudiants Natifs d'Andapa à Antsiranana) a été fondée en 2012 par un groupe d'étudiants originaires d'Andapa et des communes environnantes, poursuivant leurs études dans les établissements universitaires d'Antsiranana.

Face à l'éloignement familial, aux défis d'adaptation à la vie universitaire et au besoin de solidarité entre compatriotes, ces pionniers ont décidé de créer une structure formelle d'entraide et de cohésion sociale.

OBJECTIFS FONDATEURS
• Favoriser l'entraide mutuelle entre étudiants originaires d'Andapa
• Faciliter l'intégration des nouveaux arrivants
• Promouvoir l'excellence académique
• Préserver les valeurs culturelles communes
• Créer un réseau professionnel durable

VISION
Devenir la référence associative estudiantine à Antsiranana, reconnue pour son impact positif sur la réussite académique de ses membres et son rayonnement culturel.

MISSION ACTUELLE
L'association compte aujourd'hui des membres dans tous les établissements universitaires d'Antsiranana, répartis dans différents bâtiments universitaires. Elle organise régulièrement des activités académiques, culturelles et sportives.
"""


class HistoriqueScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        with self.canvas.before:
            Color(0.05, 0.07, 0.22, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.bg, 'size', self.size),
                  pos=lambda *a: setattr(self.bg, 'pos', self.pos))

        main = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = Button(text="◀", size_hint=(None, 1), width=dp(40),
                          background_color=(0.2, 0.3, 0.7, 1), background_normal='')
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        header.add_widget(back_btn)
        header.add_widget(Label(text="[b]📜 HISTORIQUE CENAD[/b]", markup=True,
                                 font_size=dp(15), color=(1, 0.85, 0.1, 1)))
        main.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(12),
                             size_hint_y=None, padding=(dp(5), dp(5)))
        content.bind(minimum_height=content.setter('height'))

        # Date fondation
        self._add_section_card(content, "📅 Fondée en 2012",
                                "Antsiranana, Madagascar", "#1565C0")

        # Texte historique
        hist_label = Label(
            text=HISTORIQUE_TEXT,
            font_size=dp(12),
            color=(0.85, 0.9, 1, 0.95),
            halign='left',
            text_size=(None, None),
            size_hint_y=None
        )
        hist_label.bind(width=lambda *x: setattr(hist_label, 'text_size', (hist_label.width, None)),
                         texture_size=lambda *x: setattr(hist_label, 'height', hist_label.texture_size[1]))
        content.add_widget(hist_label)

        # Présidents
        pres_title = Label(
            text="[b]👑 PRÉSIDENTS SUCCESSIFS[/b]", markup=True,
            font_size=dp(14), color=(1, 0.85, 0.1, 1),
            size_hint_y=None, height=dp(40)
        )
        content.add_widget(pres_title)

        for nom, annees, mission in PRESIDENTS:
            card = self._make_president_card(nom, annees, mission)
            content.add_widget(card)

        scroll.add_widget(content)
        main.add_widget(scroll)
        self.add_widget(main)

    def _add_section_card(self, parent, title, subtitle, color_hex):
        card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60),
                          padding=(dp(15), dp(5)))
        r, g, b = [int(color_hex.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4)]
        with card.canvas.before:
            Color(r, g, b, 0.85)
            rect = Rectangle(size=card.size, pos=card.pos)
        card.bind(size=lambda *a: setattr(rect, 'size', card.size),
                  pos=lambda *a: setattr(rect, 'pos', card.pos))
        card.add_widget(Label(text=f"[b]{title}[/b]", markup=True, font_size=dp(14),
                               color=(1, 1, 1, 1), halign='left', text_size=(dp(280), None)))
        card.add_widget(Label(text=subtitle, font_size=dp(11), color=(0.8, 0.9, 1, 0.9),
                               halign='left', text_size=(dp(280), None)))
        parent.add_widget(card)

    def _make_president_card(self, nom, annees, mission):
        card = BoxLayout(orientation='vertical', size_hint_y=None,
                          padding=(dp(15), dp(8)), spacing=dp(3))
        with card.canvas.before:
            Color(0.12, 0.18, 0.45, 0.8)
            rect = Rectangle(size=card.size, pos=card.pos)
        card.bind(size=lambda *a: setattr(rect, 'size', card.size),
                  pos=lambda *a: setattr(rect, 'pos', card.pos))

        card.add_widget(Label(text=f"[b]{nom}[/b]", markup=True, font_size=dp(13),
                               color=(1, 0.85, 0.1, 1), halign='left',
                               size_hint_y=None, height=dp(22),
                               text_size=(dp(280), None)))
        card.add_widget(Label(text=f"🗓 {annees}", font_size=dp(11),
                               color=(0.6, 0.8, 1, 1), halign='left',
                               size_hint_y=None, height=dp(18),
                               text_size=(dp(280), None)))
        mission_lbl = Label(text=mission, font_size=dp(11),
                             color=(0.75, 0.85, 1, 0.85), halign='left',
                             text_size=(None, None), size_hint_y=None)
        mission_lbl.bind(
            width=lambda *x: setattr(mission_lbl, 'text_size', (mission_lbl.width, None)),
            texture_size=lambda *x: setattr(mission_lbl, 'height', mission_lbl.texture_size[1])
        )
        card.add_widget(mission_lbl)

        def update_height(*a):
            card.height = dp(22) + dp(18) + mission_lbl.height + dp(16)
        mission_lbl.bind(height=update_height)
        card.height = dp(80)

        return card
