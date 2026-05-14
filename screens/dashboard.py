"""
screens/dashboard.py - Tableau de bord avec recherche avancee et statistiques
Amelioration: 3 filtres, tap sur membre pour detail, meilleur design
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
from kivy.graphics import Color, Rectangle, RoundedRectangle
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
            Color(0.05, 0.07, 0.25, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        main = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = Button(text="<", size_hint=(None, 1), width=dp(44),
                          background_color=(0.2, 0.3, 0.7, 1),
                          font_size=dp(18), color=(1, 1, 1, 1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        title = Label(text="[b]TABLEAU DE BORD[/b]", markup=True,
                      font_size=dp(16), color=(1, 0.85, 0.1, 1))
        header.add_widget(back_btn)
        header.add_widget(title)
        main.add_widget(header)

        # Search bar
        search_box = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        self.search_input = TextInput(
            hint_text="Rechercher par nom...",
            multiline=False,
            size_hint=(1, 1),
            background_color=(0.12, 0.16, 0.40, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.6, 0.8, 1),
            cursor_color=(1, 1, 1, 1),
            font_size=dp(13)
        )
        self.search_input.bind(text=self._on_search_text)
        search_box.add_widget(self.search_input)
        main.add_widget(search_box)

        # Filters row - 3 spinners
        filter_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))

        self.niveau_spinner = Spinner(
            text="Niveau",
            values=["Tous", "L1", "L2", "L3", "M1", "M2"],
            size_hint=(0.33, 1),
            background_color=(0.18, 0.25, 0.60, 1),
            color=(1, 1, 1, 1),
            font_size=dp(11)
        )
        self.niveau_spinner.bind(text=self._on_filter_change)

        self.batiment_spinner = Spinner(
            text="Batiment",
            values=["Tous"],
            size_hint=(0.33, 1),
            background_color=(0.18, 0.25, 0.60, 1),
            color=(1, 1, 1, 1),
            font_size=dp(11)
        )
        self.batiment_spinner.bind(text=self._on_filter_change)

        self.promotion_spinner = Spinner(
            text="Promotion",
            values=["Toutes"],
            size_hint=(0.34, 1),
            background_color=(0.18, 0.25, 0.60, 1),
            color=(1, 1, 1, 1),
            font_size=dp(11)
        )
        self.promotion_spinner.bind(text=self._on_filter_change)

        filter_box.add_widget(self.niveau_spinner)
        filter_box.add_widget(self.batiment_spinner)
        filter_box.add_widget(self.promotion_spinner)
        main.add_widget(filter_box)

        # Quick stats
        self.stats_grid = GridLayout(cols=3, size_hint_y=None, height=dp(70),
                                     spacing=dp(6))
        self.stat_total = StatCard("Total", "0", "#1565C0")
        self.stat_m = StatCard("Hommes", "0", "#2E7D32")
        self.stat_f = StatCard("Femmes", "0", "#AD1457")
        self.stats_grid.add_widget(self.stat_total)
        self.stats_grid.add_widget(self.stat_m)
        self.stats_grid.add_widget(self.stat_f)
        main.add_widget(self.stats_grid)

        # Chart buttons
        chart_bar = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(5))
        for label, field in [("Niveau", "niveau"), ("Batiment", "batiment"),
                             ("Promo", "promotion"), ("Sexe", "sexe")]:
            btn = Button(text=label, background_color=(0.20, 0.30, 0.70, 1),
                         font_size=dp(11), color=(1, 1, 1, 1))
            btn.field = field
            btn.bind(on_release=self._show_chart)
            chart_bar.add_widget(btn)
        main.add_widget(chart_bar)

        # Chart area
        self.chart_area = BoxLayout(size_hint_y=None, height=dp(0))
        self.chart_image = Image(allow_stretch=True, keep_ratio=True)
        self.chart_area.add_widget(self.chart_image)
        main.add_widget(self.chart_area)

        # Results count
        self.result_count_label = Label(
            text="[b]Resultats[/b]", markup=True,
            size_hint_y=None, height=dp(25),
            color=(0.7, 0.85, 1, 1), font_size=dp(12)
        )
        main.add_widget(self.result_count_label)

        # Results list
        scroll = ScrollView()
        self.result_list = BoxLayout(orientation='vertical', spacing=dp(4),
                                     size_hint_y=None, padding=(0, dp(4)))
        self.result_list.bind(minimum_height=self.result_list.setter('height'))
        scroll.add_widget(self.result_list)
        main.add_widget(scroll)

        self.add_widget(main)

    def on_enter(self):
        self._load_filter_values()
        self._load_stats()
        self._search()

    def _load_filter_values(self):
        batiments = db.get_distinct_values('batiment')
        self.batiment_spinner.values = ["Tous"] + batiments

        promotions = db.get_distinct_values('promotion')
        self.promotion_spinner.values = ["Toutes"] + promotions

    def _on_search_text(self, instance, value):
        if self._search_event:
            self._search_event.cancel()
        self._search_event = Clock.schedule_once(lambda dt: self._search(), 0.4)

    def _on_filter_change(self, instance, value):
        self._search()

    def _search(self):
        query = self.search_input.text.strip()
        niveau = self.niveau_spinner.text if self.niveau_spinner.text not in ("Tous", "Niveau") else ""
        batiment = self.batiment_spinner.text if self.batiment_spinner.text not in ("Tous", "Batiment") else ""
        promotion = self.promotion_spinner.text if self.promotion_spinner.text not in ("Toutes", "Promotion") else ""
        results = db.search_membres(query=query, niveau=niveau, promotion=promotion, batiment=batiment)
        self._update_list(results)

    def _update_list(self, results):
        self.result_list.clear_widgets()
        count = len(results)
        self.result_count_label.text = f"[b]Resultats ({count})[/b]"

        if not results:
            self.result_list.add_widget(
                Label(text="Aucun resultat", color=(0.6, 0.6, 0.8, 1),
                      size_hint_y=None, height=dp(40), font_size=dp(13))
            )
            return
        for m in results:
            row = MemberRow(m, on_tap=self._open_detail)
            self.result_list.add_widget(row)

    def _open_detail(self, membre):
        full = db.get_membre_by_id(membre.get('id'))
        if full and self.manager:
            detail = self.manager.get_screen('detail_membre')
            detail.set_membre(full)
            self.manager.current = 'detail_membre'

    def _load_stats(self):
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
        field = btn.field

        def generate():
            stats = db.get_stats_by_field(field)
            titles = {
                'niveau': 'Par Niveau',
                'batiment': 'Par Batiment',
                'promotion': 'Par Promotion',
                'sexe': 'Par Sexe'
            }
            if field == 'sexe':
                path = analytics.generate_pie_chart(stats, titles.get(field, field))
            else:
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
        r, g, b = self._hex_rgb(color_hex)
        with self.canvas.before:
            Color(r, g, b, 0.75)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
        self.bind(size=lambda *a: setattr(self.rect, 'size', self.size),
                  pos=lambda *a: setattr(self.rect, 'pos', self.pos))

        self.add_widget(Label(text=label, font_size=dp(10), color=(0.8, 0.9, 1, 1),
                               size_hint_y=0.4))
        self.value_label = Label(text=value, font_size=dp(22), bold=True,
                                  color=(1, 1, 1, 1), size_hint_y=0.6)
        self.add_widget(self.value_label)

    def _hex_rgb(self, h):
        h = h.lstrip('#')
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


class MemberRow(BoxLayout):
    def __init__(self, membre, on_tap=None, **kwargs):
        super().__init__(size_hint_y=None, height=dp(56), spacing=dp(8),
                         padding=(dp(10), dp(4)), **kwargs)
        self.membre = membre
        self.on_tap = on_tap

        with self.canvas.before:
            Color(0.10, 0.14, 0.38, 0.7)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(8)])
        self.bind(size=lambda *a: setattr(self.rect, 'size', self.size),
                  pos=lambda *a: setattr(self.rect, 'pos', self.pos))

        # Avatar circle
        sexe_icon = "M" if membre.get('sexe') == 'M' else "F"
        sexe_color = (0.25, 0.60, 1.00, 1) if membre.get('sexe') == 'M' else (0.90, 0.30, 0.55, 1)
        avatar = Label(text=sexe_icon, size_hint=(None, 1), width=dp(36),
                       font_size=dp(16), color=sexe_color, bold=True)
        self.add_widget(avatar)

        # Info column
        info = BoxLayout(orientation='vertical', spacing=dp(1))
        info.add_widget(Label(text=membre.get('nom', ''), font_size=dp(13),
                               color=(1, 1, 1, 1), halign='left',
                               text_size=(dp(200), None), bold=True))
        info.add_widget(Label(
            text=f"{membre.get('etablissement', '')} | {membre.get('batiment', '')}",
            font_size=dp(10), color=(0.6, 0.8, 1, 0.8), halign='left',
            text_size=(dp(200), None)
        ))
        self.add_widget(info)

        # Level badge
        niveau_lbl = Label(text=membre.get('niveau', ''), size_hint=(None, 1),
                            width=dp(40), font_size=dp(12), color=(1, 0.85, 0.1, 1),
                            bold=True)
        self.add_widget(niveau_lbl)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            with self.canvas.before:
                Color(0.25, 0.35, 0.70, 0.4)
                RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(8)])
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.on_tap:
            self.on_tap(self.membre)
            return True
        return super().on_touch_up(touch)
