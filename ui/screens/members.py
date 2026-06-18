"""
ui/screens/members.py - Écran de gestion des membres avec recherche et détails
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
import threading
import os
from config import IMAGES_DIR


class MembersScreen(Screen):
    """Écran principal de consultation des membres"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._search_timer = None
        self._built = False

    def on_enter(self):
        """Construit l'UI à la première visite"""
        if not self._built:
            self.build_ui()
            self._built = True
        self._load_members()

    def build_ui(self):
        """Construit l'interface utilisateur"""
        # Fond
        with self.canvas.before:
            Color(*self.manager.app.theme['bg_primary'])
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg)

        main = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # ===== HEADER =====
        header = self._build_header()
        main.add_widget(header)

        # ===== BARRE DE RECHERCHE =====
        search_box = self._build_search_bar()
        main.add_widget(search_box)

        # ===== STATS RAPIDES =====
        stats_box = self._build_stats()
        main.add_widget(stats_box)

        # ===== LISTE MEMBRES =====
        scroll = ScrollView()
        self.members_list = BoxLayout(
            orientation='vertical',
            spacing=dp(4),
            size_hint_y=None,
            padding=(0, dp(4))
        )
        self.members_list.bind(minimum_height=self.members_list.setter('height'))
        scroll.add_widget(self.members_list)
        main.add_widget(scroll)

        self.add_widget(main)

    def _build_header(self) -> BoxLayout:
        """Construit l'en-tête avec boutons"""
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
            text="[b]📋 ANNUAIRE[/b]",
            markup=True,
            font_size=dp(16),
            color=self.manager.app.theme['accent']
        )
        header.add_widget(title)

        return header

    def _build_search_bar(self) -> BoxLayout:
        """Construit la barre de recherche avec filtres"""
        search_box = BoxLayout(size_hint_y=None, height=dp(100), spacing=dp(5),
                               orientation='vertical')

        # Ligne 1 : Recherche textuelle
        search_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(5))

        self.search_input = TextInput(
            hint_text="Rechercher nom...",
            multiline=False,
            size_hint=(0.7, 1),
            background_color=(0.15, 0.2, 0.45, 1) if self.manager.app.current_theme.value == 'dark' else (0.9, 0.9, 0.95, 1),
            foreground_color=self.manager.app.theme['text_primary'],
            hint_text_color=self.manager.app.theme['text_secondary'],
            cursor_color=self.manager.app.theme['accent'],
            font_size=dp(12),
            write_tab=False
        )
        self.search_input.bind(text=self._on_search_text)
        search_row.add_widget(self.search_input)

        search_btn = Button(
            text="🔍",
            size_hint=(0.3, 1),
            background_color=self.manager.app.theme['accent'],
            color=self.manager.app.theme['bg_primary'],
            background_normal=''
        )
        search_btn.bind(on_release=lambda x: self._search())
        search_row.add_widget(search_btn)

        search_box.add_widget(search_row)

        # Ligne 2 : Filtres
        filters_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(5))

        self.level_spinner = Spinner(
            text="Tous niveaux",
            values=["Tous niveaux", "L1", "L2", "L3", "M1", "M2"],
            size_hint=(0.5, 1),
            background_color=self.manager.app.theme['bg_secondary'],
            color=self.manager.app.theme['text_primary'],
            font_size=dp(11)
        )
        self.level_spinner.bind(text=self._on_filter_change)
        filters_row.add_widget(self.level_spinner)

        self.building_spinner = Spinner(
            text="Tous bâtiments",
            values=["Tous bâtiments"],  # Chargé dynamiquement
            size_hint=(0.5, 1),
            background_color=self.manager.app.theme['bg_secondary'],
            color=self.manager.app.theme['text_primary'],
            font_size=dp(11)
        )
        self.building_spinner.bind(text=self._on_filter_change)
        filters_row.add_widget(self.building_spinner)

        search_box.add_widget(filters_row)

        return search_box

    def _build_stats(self) -> GridLayout:
        """Construit les cartes statistiques"""
        stats_grid = GridLayout(cols=3, size_hint_y=None, height=dp(65), spacing=dp(5))

        self.stat_total = self._make_stat_card("Total", "0", "#1565C0")
        self.stat_male = self._make_stat_card("Hommes", "0", "#2E7D32")
        self.stat_female = self._make_stat_card("Femmes", "0", "#AD1457")

        stats_grid.add_widget(self.stat_total)
        stats_grid.add_widget(self.stat_male)
        stats_grid.add_widget(self.stat_female)

        return stats_grid

    def _make_stat_card(self, label: str, value: str, color_hex: str) -> BoxLayout:
        """Crée une carte statistique"""
        card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(65))

        r, g, b = [int(color_hex.lstrip('#')[i:i+2], 16) / 255 for i in (0, 2, 4)]

        with card.canvas.before:
            Color(r, g, b, 0.8)
            self.card_rect = Rectangle(size=card.size, pos=card.pos)
        card.bind(size=lambda *a: setattr(self.card_rect, 'size', card.size),
                  pos=lambda *a: setattr(self.card_rect, 'pos', card.pos))

        label_widget = Label(
            text=label,
            font_size=dp(10),
            color=self.manager.app.theme['text_primary'],
            size_hint_y=0.4
        )
        card.add_widget(label_widget)

        value_widget = Label(
            text=value,
            font_size=dp(18),
            bold=True,
            color=self.manager.app.theme['text_primary'],
            size_hint_y=0.6
        )
        card.add_widget(value_widget)

        # Sauvegarder référence pour mise à jour
        card.value_label = value_widget

        return card

    def _on_search_text(self, instance, value):
        """Lancé à chaque caractère, avec debounce"""
        if self._search_timer:
            self._search_timer.cancel()
        self._search_timer = Clock.schedule_once(lambda dt: self._search(), 0.4)

    def _on_filter_change(self, instance, value):
        """Lancé quand un filtre change"""
        self._search()

    def _load_members(self):
        """Charge les membres et les stats"""
        def load():
            members = self.manager.app.db.get_membres()
            stats = self._compute_stats()
            Clock.schedule_once(lambda dt: self._display_members(members, stats))

        threading.Thread(target=load, daemon=True).start()

    def _search(self):
        """Effectue la recherche avec filtres"""
        query = self.search_input.text.strip()
        level = None if self.level_spinner.text == "Tous niveaux" else self.level_spinner.text
        building = None if self.building_spinner.text == "Tous bâtiments" else self.building_spinner.text

        results = self.manager.app.db.search_membres(
            query=query,
            niveau=level,
            batiment=building
        )

        self._update_members_list(results)

    def _display_members(self, members, stats):
        """Affiche les membres et stats"""
        self._update_members_list(members)
        self._update_stats(stats)

        # Charger les bâtiments uniques pour le spinner
        self._load_buildings()

    def _load_buildings(self):
        """Charge les bâtiments uniques"""
        buildings = set()
        members = self.manager.app.db.get_membres()
        for m in members:
            if m.get('batiment'):
                buildings.add(m['batiment'])

        building_list = ["Tous bâtiments"] + sorted(list(buildings))
        self.building_spinner.values = building_list

    def _update_members_list(self, members):
        """Met à jour l'affichage de la liste"""
        self.members_list.clear_widgets()

        if not members:
            self.members_list.add_widget(Label(
                text="Aucun résultat",
                color=self.manager.app.theme['text_secondary'],
                size_hint_y=None,
                height=dp(40),
                font_size=dp(12)
            ))
            return

        for member in members:
            card = MemberCard(member, self._on_member_click, self.manager.app.theme)
            self.members_list.add_widget(card)

    def _update_stats(self, stats):
        """Met à jour les statistiques"""
        self.stat_total.value_label.text = str(stats['total'])
        self.stat_male.value_label.text = str(stats['male'])
        self.stat_female.value_label.text = str(stats['female'])

    def _compute_stats(self) -> dict:
        """Calcule les statistiques"""
        members = self.manager.app.db.get_membres()
        total = len(members)
        male = sum(1 for m in members if m.get('sexe') == 'M')
        female = total - male

        return {
            'total': total,
            'male': male,
            'female': female
        }

    def _on_member_click(self, member):
        """Ouvre le détail d'un membre"""
        popup = MemberDetailPopup(member, self.manager.app.theme, self.manager.app.db)
        popup.open()

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos


class MemberCard(BoxLayout):
    """Carte d'affichage d'un membre"""

    def __init__(self, member: dict, on_click_callback, theme: dict, **kwargs):
        super().__init__(
            size_hint_y=None,
            height=dp(60),
            spacing=dp(8),
            padding=dp(8),
            **kwargs
        )
        self.member = member
        self.on_click = on_click_callback

        # Fond coloré
        with self.canvas.before:
            Color(*theme['bg_secondary'])
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.rect, 'size', self.size),
                  pos=lambda *a: setattr(self.rect, 'pos', self.pos))

        # Icône sexe
        sexe_text = "♂" if member.get('sexe') == 'M' else "♀"
        sexe_color = (0.4, 0.8, 1, 1) if member.get('sexe') == 'M' else (1, 0.6, 0.8, 1)

        self.add_widget(Label(
            text=sexe_text,
            size_hint=(None, 1),
            width=dp(25),
            font_size=dp(14),
            color=sexe_color
        ))

        # Infos textuelles
        info_box = BoxLayout(orientation='vertical', size_hint=(0.7, 1), spacing=dp(2))

        nom_complet = f"{member.get('prenom', '')} {member.get('nom', '')}".strip()
        info_box.add_widget(Label(
            text=nom_complet,
            font_size=dp(12),
            bold=True,
            color=theme['text_primary'],
            halign='left',
            text_size=(None, None),
            size_hint_y=0.6
        ))

        detail_text = f"{member.get('etablissement', '')} | {member.get('niveau', '')}"
        info_box.add_widget(Label(
            text=detail_text,
            font_size=dp(10),
            color=theme['text_secondary'],
            halign='left',
            text_size=(None, None),
            size_hint_y=0.4
        ))

        self.add_widget(info_box)

        # Bouton détail
        detail_btn = Button(
            text="▶",
            size_hint=(None, 1),
            width=dp(35),
            background_color=theme['accent'],
            color=theme['bg_primary'],
            background_normal=''
        )
        detail_btn.bind(on_release=lambda x: on_click_callback(member))
        self.add_widget(detail_btn)


class MemberDetailPopup(Popup):
    """Fenêtre de détail d'un membre"""

    def __init__(self, member: dict, theme: dict, db, **kwargs):
        self.member = member
        self.theme = theme
        self.db = db

        content = self._build_content()

        super().__init__(
            title=f"{member.get('prenom', '')} {member.get('nom', '')}",
            content=content,
            size_hint=(0.95, 0.85),
            background_color=theme['bg_primary'],
            **kwargs
        )

    def _build_content(self) -> BoxLayout:
        """Construit le contenu du popup"""
        main = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        # Photo si disponible
        photo_filename = self.member.get('photo_filename', '')
        if photo_filename:
            photo_path = os.path.join(IMAGES_DIR, photo_filename)
            if os.path.exists(photo_path):
                photo_box = BoxLayout(size_hint_y=None, height=dp(150))
                photo_box.add_widget(Image(
                    source=photo_path,
                    allow_stretch=True,
                    keep_ratio=True
                ))
                main.add_widget(photo_box)

        # ScrollView pour les détails
        scroll = ScrollView()
        details = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        details.bind(minimum_height=details.setter('height'))

        # Détails
        details_list = [
            ("Nom complet", f"{self.member.get('prenom', '')} {self.member.get('nom', '')}"),
            ("Sexe", "Masculin" if self.member.get('sexe') == 'M' else "Féminin"),
            ("Niveau", self.member.get('niveau', '')),
            ("Promotion", self.member.get('promotion', '')),
            ("Établissement", self.member.get('etablissement', '')),
            ("Bâtiment", self.member.get('batiment', '')),
            ("Commune", self.member.get('commune_origine', '')),
            ("Téléphone", self.member.get('telephone', 'Non disponible')),
        ]

        for label, value in details_list:
            detail_row = self._make_detail_row(label, value)
            details.add_widget(detail_row)

        scroll.add_widget(details)
        main.add_widget(scroll)

        # Boutons d'action
        action_box = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(5))

        edit_btn = Button(
            text="Modifier",
            background_color=(0.15, 0.5, 0.85, 1),
            color=self.theme['text_primary'],
            background_normal=''
        )
        edit_btn.bind(on_release=self._on_edit)
        action_box.add_widget(edit_btn)

        close_btn = Button(
            text="Fermer",
            background_color=self.theme['bg_secondary'],
            color=self.theme['text_primary'],
            background_normal=''
        )
        close_btn.bind(on_release=self.dismiss)
        action_box.add_widget(close_btn)

        main.add_widget(action_box)

        return main

    def _make_detail_row(self, label: str, value: str) -> BoxLayout:
        """Crée une ligne de détail"""
        row = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(40), spacing=dp(2))

        row.add_widget(Label(
            text=f"[b]{label}[/b]",
            markup=True,
            font_size=dp(10),
            color=self.theme['accent'],
            halign='left',
            size_hint_y=0.4
        ))

        row.add_widget(Label(
            text=value,
            font_size=dp(12),
            color=self.theme['text_primary'],
            halign='left',
            text_size=(None, None),
            size_hint_y=0.6
        ))

        return row

    def _on_edit(self, *args):
        """Édition non disponible pour l'instant"""
        self.dismiss()
