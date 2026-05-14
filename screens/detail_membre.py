"""
screens/detail_membre.py - Ecran de detail d'un membre
Affiche le profil complet avec toutes les informations.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.metrics import dp


class DetailMembreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._membre = None

    def set_membre(self, membre):
        self._membre = membre
        self.clear_widgets()
        self._build_ui()

    def _build_ui(self):
        m = self._membre
        if not m:
            return

        with self.canvas.before:
            Color(0.05, 0.07, 0.25, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.bg, 'size', self.size),
                  pos=lambda *a: setattr(self.bg, 'pos', self.pos))

        main = BoxLayout(orientation='vertical', padding=dp(0), spacing=dp(0))

        # Header with back button
        header = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10),
                           padding=(dp(8), dp(6)))
        with header.canvas.before:
            Color(0.04, 0.06, 0.20, 1)
            h_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda *a: setattr(h_rect, 'size', header.size),
                    pos=lambda *a: setattr(h_rect, 'pos', header.pos))

        back_btn = Button(text="<", size_hint=(None, 1), width=dp(44),
                          background_color=(0.2, 0.3, 0.7, 1),
                          font_size=dp(18), color=(1, 1, 1, 1))
        back_btn.bind(on_release=self._go_back)
        header.add_widget(back_btn)
        header.add_widget(Label(text="[b]PROFIL MEMBRE[/b]", markup=True,
                                font_size=dp(16), color=(1, 0.85, 0.1, 1)))
        header.add_widget(Widget(size_hint_x=None, width=dp(44)))
        main.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None,
                            padding=(dp(16), dp(16)), spacing=dp(12))
        content.bind(minimum_height=content.setter('height'))

        # Profile avatar area
        avatar_box = BoxLayout(orientation='vertical', size_hint_y=None,
                               height=dp(160), padding=(0, dp(10)))
        avatar_container = BoxLayout(size_hint=(None, None), size=(dp(80), dp(80)),
                                     pos_hint={'center_x': 0.5})
        with avatar_container.canvas.before:
            sexe_color = (0.25, 0.60, 1.00, 1) if m.get('sexe') == 'M' else (0.90, 0.30, 0.55, 1)
            Color(*sexe_color)
            avatar_bg = Ellipse(size=avatar_container.size, pos=avatar_container.pos)
        avatar_container.bind(
            size=lambda *a: setattr(avatar_bg, 'size', avatar_container.size),
            pos=lambda *a: setattr(avatar_bg, 'pos', avatar_container.pos)
        )

        initials = self._get_initials(m.get('nom', ''))
        avatar_container.add_widget(Label(
            text=initials, font_size=dp(28), bold=True,
            color=(1, 1, 1, 1)
        ))
        avatar_box.add_widget(avatar_container)

        # Name
        avatar_box.add_widget(Label(
            text=f"[b]{m.get('nom', '')}[/b]", markup=True,
            font_size=dp(18), color=(1, 1, 1, 1),
            size_hint_y=None, height=dp(30), halign='center'
        ))

        # Sexe badge
        sexe_text = "Homme" if m.get('sexe') == 'M' else "Femme"
        sexe_icon = "M" if m.get('sexe') == 'M' else "F"
        avatar_box.add_widget(Label(
            text=f"{sexe_icon} | {sexe_text}",
            font_size=dp(12), color=(0.7, 0.85, 1, 0.9),
            size_hint_y=None, height=dp(20), halign='center'
        ))
        content.add_widget(avatar_box)

        # Info cards
        info_items = [
            ("Niveau", m.get('niveau', 'N/A'), "#1565C0"),
            ("Promotion", m.get('promotion', 'N/A'), "#6A1B9A"),
            ("Batiment", m.get('batiment', 'N/A'), "#2E7D32"),
            ("Etablissement", m.get('etablissement', 'N/A'), "#BF360C"),
            ("Commune d'origine", m.get('commune_origine', 'N/A'), "#006064"),
            ("Telephone", m.get('telephone', 'N/A'), "#37474F"),
        ]

        for label, value, color_hex in info_items:
            card = self._make_info_card(label, value, color_hex)
            content.add_widget(card)

        content.add_widget(Widget(size_hint_y=None, height=dp(20)))

        scroll.add_widget(content)
        main.add_widget(scroll)
        self.add_widget(main)

    def _make_info_card(self, label, value, color_hex):
        card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(62),
                         padding=(dp(16), dp(8)), spacing=dp(2))
        r, g, b = [int(color_hex.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        with card.canvas.before:
            Color(r, g, b, 0.25)
            rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[dp(10)])
        card.bind(size=lambda *a: setattr(rect, 'size', card.size),
                  pos=lambda *a: setattr(rect, 'pos', card.pos))

        # Left accent bar
        with card.canvas.before:
            Color(r, g, b, 1)
            accent = RoundedRectangle(
                pos=(card.pos[0], card.pos[1]),
                size=(dp(4), card.size[1]),
                radius=[dp(2)]
            )
        card.bind(
            pos=lambda *a: setattr(accent, 'pos', (card.pos[0], card.pos[1])),
            size=lambda *a: setattr(accent, 'size', (dp(4), card.size[1]))
        )

        card.add_widget(Label(
            text=label.upper(), font_size=dp(10), color=(0.6, 0.7, 0.9, 0.8),
            halign='left', size_hint_y=None, height=dp(16),
            text_size=(dp(280), None), bold=True
        ))
        card.add_widget(Label(
            text=str(value) if value else "Non renseigne",
            font_size=dp(15), color=(1, 1, 1, 1),
            halign='left', size_hint_y=None, height=dp(22),
            text_size=(dp(280), None), bold=True
        ))
        return card

    def _get_initials(self, nom):
        parts = nom.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        elif parts:
            return parts[0][:2].upper()
        return "?"

    def _go_back(self, *args):
        if self.manager:
            self.manager.current = self.manager.previous()
