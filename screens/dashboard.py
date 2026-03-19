"""
screens/dashboard.py - Tableau de bord avec recherche et statistiques
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.metrics import dp
import threading
import os

import db_manager as db
import analytics


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._search_event = None
        self.build_ui()

    def build_ui(self):
        with self.canvas.before:
            Color(0.07, 0.09, 0.30, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        main = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # Titre
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = Button(text="◀", size_hint=(None, 1), width=dp(40),
                          background_color=(0.2, 0.3, 0.7, 1),
                          background_normal='')
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        title = Label(text="[b]📊 TABLEAU DE BORD[/b]", markup=True,
                      font_size=dp(16), color=(1, 0.85, 0.1, 1))
        header.add_widget(back_btn)
        header.add_widget(title)
        main.add_widget(header)

        # Barre recherche
        search_box = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(5))
        self.search_input = TextInput(
            hint_text="🔎 Rechercher par nom...",
            multiline=False,
            size_hint=(0.6, 1),
            background_color=(0.15, 0.2, 0.45, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.6, 0.8, 1),
            cursor_color=(1, 1, 1, 1),
            font_size=dp(13)
        )
        self.search_input.bind(text=self._on_search_text)

        self.niveau_spinner = Spinner(
            text="Niveau",
            values=["Tous", "L1", "L2", "L3", "M1", "M2"],
            size_hint=(0.2, 1),
            background_color=(0.2, 0.3, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size=dp(12)
        )
        self.niveau_spinner.bind(text=self._on_filter_change)

        search_box.add_widget(self.search_input)
        search_box.add_widget(self.niveau_spinner)
        main.add_widget(search_box)

        # Stats rapides
        self.stats_grid = GridLayout(cols=3, size_hint_y=None, height=dp(75),
                                     spacing=dp(5))
        self.stat_total = StatCard("Total", "0", "#1565C0")
        self.stat_m = StatCard("Hommes", "0", "#2E7D32")
        self.stat_f = StatCard("Femmes", "0", "#AD1457")
        self.stats_grid.add_widget(self.stat_total)
        self.stats_grid.add_widget(self.stat_m)
        self.stats_grid.add_widget(self.stat_f)
        main.add_widget(self.stats_grid)

        # Boutons graphiques
        chart_bar = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        for label, field in [("Par Niveau", "niveau"), ("Par Bâtiment", "batiment"), ("Par Promo", "promotion")]:
            btn = Button(text=label, background_color=(0.25, 0.4, 0.9, 1),
                         background_normal='', font_size=dp(11), color=(1, 1, 1, 1))
            btn.field = field
            btn.bind(on_release=self._show_chart)
            chart_bar.add_widget(btn)
        main.add_widget(chart_bar)

        # Zone graphique
        self.chart_area = BoxLayout(size_hint_y=None, height=dp(0))
        self.chart_image = Image(allow_stretch=True, keep_ratio=True)
        self.chart_area.add_widget(self.chart_image)
        main.add_widget(self.chart_area)

        # Liste résultats
        result_label = Label(text="[b]Résultats[/b]", markup=True,
                             size_hint_y=None, height=dp(25),
                             color=(0.7, 0.85, 1, 1), font_size=dp(12))
        main.add_widget(result_label)

        scroll = ScrollView()
        self.result_list = BoxLayout(orientation='vertical', spacing=dp(4),
                                     size_hint_y=None, padding=(0, dp(4)))
        self.result_list.bind(minimum_height=self.result_list.setter('height'))
        scroll.add_widget(self.result_list)
        main.add_widget(scroll)

        self.add_widget(main)

    def on_enter(self):
        """Chargement au premier affichage."""
        self._load_stats()
        self._search()

    def _on_search_text(self, instance, value):
        """Recherche avec délai (debounce 400ms)."""
        if self._search_event:
            self._search_event.cancel()
        self._search_event = Clock.schedule_once(lambda dt: self._search(), 0.4)

    def _on_filter_change(self, instance, value):
        self._search()

    def _search(self):
        query = self.search_input.text.strip()
        niveau = self.niveau_spinner.text if self.niveau_spinner.text != "Tous" else ""
        results = db.search_membres(query=query, niveau=niveau)
        self._update_list(results)

    def _update_list(self, results):
        self.result_list.clear_widgets()
        if not results:
            self.result_list.add_widget(
                Label(text="Aucun résultat", color=(0.6, 0.6, 0.8, 1),
                      size_hint_y=None, height=dp(40), font_size=dp(13))
            )
            return
        for m in results:
            row = MemberRow(m)
            self.result_list.add_widget(row)

    def _load_stats(self):
        """Charge les statistiques en arrière-plan."""
        def load():
            stats = analytics.compute_stats()
            Clock.schedule_once(lambda dt: self._display_stats(stats))

        threading.Thread(target=load, daemon=True).start()

    def _display_stats(self, stats):
        self.stat_total.value_label.text = str(stats.get('total', 0))
        sexe = stats.get('par_sexe', {})
        self.stat_m.value_label.text = str(sexe.get('M', 0))
        self.stat_f.value_label.text = str(sexe.get('F', 0))

    def _show_chart(self, btn):
        """Génère et affiche un graphique à la demande."""
        field = btn.field

        def generate():
            stats = db.get_stats_by_field(field)
            titles = {'niveau': 'Par Niveau', 'batiment': 'Par Bâtiment', 'promotion': 'Par Promotion'}
            path = analytics.generate_bar_chart(stats, titles.get(field, field), field, "Membres")
            if path:
                Clock.schedule_once(lambda dt: self._display_chart(path))

        threading.Thread(target=generate, daemon=True).start()

    def _display_chart(self, path):
        self.chart_area.height = dp(220)
        self.chart_image.source = path
        self.chart_image.reload()

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos


class StatCard(BoxLayout):
    def __init__(self, label, value, color_hex, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        with self.canvas.before:
            r, g, b = self._hex_rgb(color_hex)
            Color(r, g, b, 0.8)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.rect, 'size', self.size),
                  pos=lambda *a: setattr(self.rect, 'pos', self.pos))

        self.add_widget(Label(text=label, font_size=dp(10), color=(0.8, 0.9, 1, 1),
                               size_hint_y=0.4))
        self.value_label = Label(text=value, font_size=dp(20), bold=True,
                                  color=(1, 1, 1, 1), size_hint_y=0.6)
        self.add_widget(self.value_label)

    def _hex_rgb(self, h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))


class MemberRow(BoxLayout):
    def __init__(self, membre, **kwargs):
        super().__init__(size_hint_y=None, height=dp(48), spacing=dp(5), **kwargs)
        with self.canvas.before:
            Color(0.1, 0.15, 0.4, 0.7)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.rect, 'size', self.size),
                  pos=lambda *a: setattr(self.rect, 'pos', self.pos))

        sexe_icon = "♂" if membre.get('sexe') == 'M' else "♀"
        sexe_color = (0.4, 0.8, 1, 1) if membre.get('sexe') == 'M' else (1, 0.6, 0.8, 1)

        self.add_widget(Label(text=sexe_icon, size_hint=(None, 1), width=dp(25),
                               font_size=dp(16), color=sexe_color))

        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(text=membre.get('nom', ''), font_size=dp(13),
                               color=(1, 1, 1, 1), halign='left', text_size=(dp(200), None)))
        info.add_widget(Label(
            text=f"{membre.get('etablissement', '')} | {membre.get('batiment', '')}",
            font_size=dp(10), color=(0.6, 0.8, 1, 0.8), halign='left',
            text_size=(dp(200), None)
        ))
        self.add_widget(info)

        niveau_lbl = Label(text=membre.get('niveau', ''), size_hint=(None, 1), width=dp(40),
                            font_size=dp(12), color=(1, 0.85, 0.1, 1),
                            bold=True)
        self.add_widget(niveau_lbl)
