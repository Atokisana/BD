"""
screens/liste_batiment.py - Liste des membres groupés par bâtiment
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
import db_manager as db


class ListeBatimentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._built = False

    def on_enter(self):
        if not self._built:
            self._build_ui()
            self._built = True
        else:
            self._load_data()

    def _build_ui(self):
        with self.canvas.before:
            Color(0.07, 0.09, 0.30, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.bg, 'size', self.size),
                  pos=lambda *a: setattr(self.bg, 'pos', self.pos))

        main = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = Button(text="◀", size_hint=(None, 1), width=dp(40),
                          background_color=(0.2, 0.3, 0.7, 1), background_normal='')
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        header.add_widget(back_btn)
        header.add_widget(Label(text="[b] LISTE PAR BÂTIMENT[/b]", markup=True,
                                 font_size=dp(15), color=(1, 0.85, 0.1, 1)))
        main.add_widget(header)

        scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', spacing=dp(10),
                                  size_hint_y=None, padding=(0, dp(5)))
        self.content.bind(minimum_height=self.content.setter('height'))
        scroll.add_widget(self.content)
        main.add_widget(scroll)

        self.add_widget(main)
        self._load_data()

    def _load_data(self):
        self.content.clear_widgets()
        # Requête SQL GROUP BY directe
        import db_manager as db
        import sqlite3
        conn = db.get_connection()
        batiments = conn.execute(
            "SELECT batiment, COUNT(*) as total FROM membres GROUP BY batiment ORDER BY batiment"
        ).fetchall()
        conn.close()

        colors = ['#1565C0', '#2E7D32', '#4A148C', '#BF360C', '#006064', '#37474F']
        for i, row in enumerate(batiments):
            batiment_name = row['batiment'] or 'Non défini'
            total = row['total']
            color = colors[i % len(colors)]
            section = BatimentSection(batiment_name, total, color)
            self.content.add_widget(section)


class BatimentSection(BoxLayout):
    def __init__(self, batiment_name, total, color_hex, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, spacing=dp(4), **kwargs)

        # En-tête bâtiment
        header_h = dp(50)
        header = BoxLayout(size_hint_y=None, height=header_h, padding=(dp(15), 0))
        with header.canvas.before:
            r, g, b = [int(color_hex.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4)]
            Color(r, g, b, 0.9)
            self.h_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda *a: setattr(self.h_rect, 'size', header.size),
                    pos=lambda *a: setattr(self.h_rect, 'pos', header.pos))

        header.add_widget(Label(
            text=f"[b] {batiment_name}[/b]   ({total} membre{'s' if total > 1 else ''})",
            markup=True, font_size=dp(14), color=(1, 1, 1, 1), halign='left'
        ))
        self.add_widget(header)

        # Liste membres du bâtiment
        conn_obj = __import__('db_manager').get_connection()
        membres = conn_obj.execute(
            "SELECT nom, sexe, niveau, promotion, etablissement FROM membres WHERE batiment=? ORDER BY nom",
            (batiment_name,)
        ).fetchall()
        conn_obj.close()

        for m in membres:
            row = BoxLayout(size_hint_y=None, height=dp(38), padding=(dp(20), 0),
                            spacing=dp(5))
            with row.canvas.before:
                Color(0.1, 0.15, 0.4, 0.5)
                r2 = Rectangle(size=row.size, pos=row.pos)
            row.bind(size=lambda *a, r=r2: setattr(r, 'size', row.size),
                     pos=lambda *a, r=r2: setattr(r, 'pos', row.pos))

            sexe_icon = "♂" if m['sexe'] == 'M' else "♀"
            sexe_col = (0.4, 0.8, 1, 1) if m['sexe'] == 'M' else (1, 0.6, 0.8, 1)
            row.add_widget(Label(text=sexe_icon, size_hint=(None, 1), width=dp(20),
                                  font_size=dp(14), color=sexe_col))
            row.add_widget(Label(text=m['nom'], font_size=dp(12), color=(1, 1, 1, 1),
                                  halign='left', text_size=(dp(180), None)))
            row.add_widget(Label(text=f"{m['niveau']} | {m['promotion']}",
                                  font_size=dp(11), color=(1, 0.85, 0.1, 0.9),
                                  size_hint=(None, 1), width=dp(90)))
            self.add_widget(row)

        # Mise à jour hauteur
        self.height = header_h + len(membres) * dp(38) + dp(10)
