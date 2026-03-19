"""
screens/liste_promotion.py - Liste des membres groupés par promotion
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp


class ListePromotionScreen(Screen):
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
        header.add_widget(Label(text="[b]🎓 LISTE PAR PROMOTION[/b]", markup=True,
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
        import db_manager as db
        conn = db.get_connection()
        promotions = conn.execute(
            "SELECT promotion, COUNT(*) as total FROM membres GROUP BY promotion ORDER BY promotion DESC"
        ).fetchall()
        conn.close()

        gradient_colors = ['#6A1B9A', '#283593', '#1565C0', '#0277BD', '#00695C', '#2E7D32']
        for i, row in enumerate(promotions):
            promo = row['promotion'] or 'Non défini'
            total = row['total']
            color = gradient_colors[i % len(gradient_colors)]
            section = PromotionSection(promo, total, color)
            self.content.add_widget(section)


class PromotionSection(BoxLayout):
    def __init__(self, promo, total, color_hex, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, spacing=dp(3), **kwargs)

        # En-tête promotion
        header_h = dp(55)
        header = BoxLayout(size_hint_y=None, height=header_h, padding=(dp(15), 0),
                            spacing=dp(10))
        with header.canvas.before:
            r, g, b = [int(color_hex.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4)]
            Color(r, g, b, 0.9)
            h_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda *a: setattr(h_rect, 'size', header.size),
                    pos=lambda *a: setattr(h_rect, 'pos', header.pos))

        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(text=f"[b]🎓 Promotion {promo}[/b]", markup=True,
                               font_size=dp(14), color=(1, 1, 1, 1), halign='left',
                               text_size=(dp(200), None)))
        info.add_widget(Label(text=f"{total} membre{'s' if total > 1 else ''}",
                               font_size=dp(11), color=(0.8, 0.9, 1, 0.9), halign='left',
                               text_size=(dp(200), None)))
        header.add_widget(info)
        self.add_widget(header)

        # Liste membres de cette promotion
        conn = __import__('db_manager').get_connection()
        membres = conn.execute(
            "SELECT nom, sexe, niveau, batiment, etablissement FROM membres WHERE promotion=? ORDER BY niveau, nom",
            (promo,)
        ).fetchall()
        conn.close()

        for m in membres:
            row = BoxLayout(size_hint_y=None, height=dp(40), padding=(dp(20), 0),
                            spacing=dp(5))
            with row.canvas.before:
                Color(0.1, 0.12, 0.38, 0.5)
                r2 = Rectangle(size=row.size, pos=row.pos)
            row.bind(size=lambda *a, r=r2: setattr(r, 'size', row.size),
                     pos=lambda *a, r=r2: setattr(r, 'pos', row.pos))

            sexe_icon = "♂" if m['sexe'] == 'M' else "♀"
            sexe_col = (0.4, 0.8, 1, 1) if m['sexe'] == 'M' else (1, 0.6, 0.8, 1)
            row.add_widget(Label(text=sexe_icon, size_hint=(None, 1), width=dp(20),
                                  font_size=dp(14), color=sexe_col))

            name_box = BoxLayout(orientation='vertical')
            name_box.add_widget(Label(text=m['nom'], font_size=dp(12),
                                       color=(1, 1, 1, 1), halign='left',
                                       text_size=(dp(180), None)))
            name_box.add_widget(Label(text=f"{m['etablissement']} | {m['batiment']}",
                                       font_size=dp(10), color=(0.6, 0.8, 1, 0.8),
                                       halign='left', text_size=(dp(180), None)))
            row.add_widget(name_box)

            row.add_widget(Label(text=m['niveau'], size_hint=(None, 1), width=dp(35),
                                  font_size=dp(12), color=(1, 0.85, 0.1, 1), bold=True))
            self.add_widget(row)

        self.height = header_h + len(membres) * dp(40) + dp(8)
