"""
ui/screens/settings.py - Écran des paramètres de l'application
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
import threading
import os
from config import Theme
from data.importer import ZIPImporter


class SettingsScreen(Screen):
    """Écran de configuration de l'application"""

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
            text="[b]⚙ PARAMÈTRES[/b]",
            markup=True,
            font_size=dp(16),
            color=self.manager.app.theme['accent']
        )
        header.add_widget(title)

        main.add_widget(header)

        # ===== SCROLL CONTENT =====
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=dp(10))
        content.bind(minimum_height=content.setter('height'))

        # ===== SECTION : THÈME =====
        content.add_widget(self._build_section_title("Apparence"))

        theme_box = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10), orientation='vertical')
        theme_row = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(10))

        theme_row.add_widget(Label(
            text="Mode sombre",
            font_size=dp(12),
            color=self.manager.app.theme['text_primary'],
            size_hint_x=0.7
        ))

        theme_switch = Switch(
            active=self.manager.app.current_theme == Theme.DARK,
            size_hint_x=0.3
        )
        theme_switch.bind(active=self._on_theme_toggle)
        theme_row.add_widget(theme_switch)

        theme_box.add_widget(theme_row)

        current_theme = "Mode sombre activé" if self.manager.app.current_theme == Theme.DARK else "Mode clair activé"
        theme_box.add_widget(Label(
            text=f"[i]{current_theme}[/i]",
            markup=True,
            font_size=dp(10),
            color=self.manager.app.theme['text_secondary'],
            size_hint_y=None,
            height=dp(20)
        ))

        content.add_widget(theme_box)

        # ===== SECTION : DONNÉES =====
        content.add_widget(self._build_section_title("Gestion des données"))

        # Import ZIP
        import_btn = Button(
            text="📥 Importer ZIP (CSV + photos)",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.15, 0.5, 0.85, 1),
            color=self.manager.app.theme['text_primary'],
            background_normal=''
        )
        import_btn.bind(on_release=self._on_import_zip)
        content.add_widget(import_btn)

        # Réinitialiser BD
        reset_btn = Button(
            text="🔄 Réinitialiser la base de données",
            size_hint_y=None,
            height=dp(50),
            background_color=self.manager.app.theme['error'],
            color=(1, 1, 1, 1),
            background_normal=''
        )
        reset_btn.bind(on_release=self._on_reset_db)
        content.add_widget(reset_btn)

        # ===== SECTION : STATS =====
        content.add_widget(self._build_section_title("Statistiques"))

        stats_box = BoxLayout(size_hint_y=None, height=dp(80), orientation='vertical', spacing=dp(5))

        total_members = self.manager.app.db.get_total_count()
        stats_box.add_widget(Label(
            text=f"Total de membres : {total_members}",
            font_size=dp(12),
            color=self.manager.app.theme['text_primary'],
            size_hint_y=None,
            height=dp(30)
        ))

        stats_box.add_widget(Label(
            text=f"Version BD : {self.manager.app.db.VERSION}",
            font_size=dp(12),
            color=self.manager.app.theme['text_primary'],
            size_hint_y=None,
            height=dp(30)
        ))

        content.add_widget(stats_box)

        # ===== SECTION : ABOUT =====
        content.add_widget(self._build_section_title("À propos"))

        about_btn = Button(
            text="ℹ À propos de l'application",
            size_hint_y=None,
            height=dp(50),
            background_color=self.manager.app.theme['bg_secondary'],
            color=self.manager.app.theme['text_primary'],
            background_normal=''
        )
        about_btn.bind(on_release=self._on_about)
        content.add_widget(about_btn)

        scroll.add_widget(content)
        main.add_widget(scroll)

        self.add_widget(main)

    def _build_section_title(self, title: str) -> Label:
        """Crée un titre de section"""
        return Label(
            text=f"[b]{title}[/b]",
            markup=True,
            font_size=dp(13),
            bold=True,
            color=self.manager.app.theme['accent'],
            size_hint_y=None,
            height=dp(30)
        )

    def _on_theme_toggle(self, instance, value):
        """Bascule le thème"""
        self.manager.app.switch_theme()
        Clock.schedule_once(lambda dt: self._refresh_screen(), 0.1)

    def _refresh_screen(self):
        """Rafraîchit l'écran avec le nouveau thème"""
        self.manager.current = 'settings'

    def _on_import_zip(self, *args):
        """Ouvre le sélecteur de fichier ZIP"""
        content = BoxLayout(orientation='vertical')

        filechooser = FileChooserListView(filters=['*.zip'])
        content.add_widget(filechooser)

        button_box = BoxLayout(size_hint_y=0.1, spacing=dp(10), padding=dp(10))

        def on_import():
            if filechooser.selection:
                zip_path = filechooser.selection[0]
                self._import_zip_file(zip_path)
                popup.dismiss()

        def on_cancel():
            popup.dismiss()

        import_btn = Button(text="Importer", background_normal='', background_color=(0.13, 0.55, 0.13, 1))
        cancel_btn = Button(text="Annuler", background_normal='', background_color=(0.4, 0.1, 0.1, 1))

        import_btn.bind(on_release=lambda x: on_import())
        cancel_btn.bind(on_release=lambda x: on_cancel())

        button_box.add_widget(import_btn)
        button_box.add_widget(cancel_btn)

        content.add_widget(button_box)

        popup = Popup(
            title="Sélectionner un fichier ZIP",
            content=content,
            size_hint=(0.9, 0.9)
        )
        popup.open()

    def _import_zip_file(self, zip_path: str):
        """Effectue l'import ZIP"""
        def import_thread():
            importer = ZIPImporter(self.manager.app.db)
            report = importer.import_zip(zip_path)
            Clock.schedule_once(lambda dt: self._show_import_report(report))

        threading.Thread(target=import_thread, daemon=True).start()

        # Afficher loading
        loading_popup = Popup(
            title="Import en cours...",
            content=Label(text="Veuillez patienter"),
            size_hint=(0.8, 0.4)
        )
        loading_popup.open()

    def _show_import_report(self, report: dict):
        """Affiche un rapport d'import"""
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        title = Label(
            text="[b]Rapport d'import[/b]",
            markup=True,
            font_size=dp(14),
            color=self.manager.app.theme['accent'],
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(title)

        stats = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), spacing=dp(5))

        stats.add_widget(Label(
            text=f"✓ Succès : {report.get('success', 0)}",
            font_size=dp(12),
            color=self.manager.app.theme['success'],
            size_hint_y=None,
            height=dp(25)
        ))

        stats.add_widget(Label(
            text=f"⚠ Avertissements : {report.get('warnings', 0)}",
            font_size=dp(12),
            color=(1, 0.85, 0.1, 1),
            size_hint_y=None,
            height=dp(25)
        ))

        stats.add_widget(Label(
            text=f"✗ Erreurs : {report.get('errors', 0)}",
            font_size=dp(12),
            color=self.manager.app.theme['error'],
            size_hint_y=None,
            height=dp(25)
        ))

        content.add_widget(stats)

        # Messages
        scroll = ScrollView(size_hint_y=0.6)
        messages_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(3), padding=(0, dp(5)))
        messages_box.bind(minimum_height=messages_box.setter('height'))

        for msg in report.get('messages', []):
            msg_label = Label(
                text=msg,
                font_size=dp(10),
                color=self.manager.app.theme['text_secondary'],
                halign='left',
                text_size=(None, None),
                size_hint_y=None
            )
            msg_label.bind(
                width=lambda *x, ml=msg_label: setattr(ml, 'text_size', (ml.width, None)),
                texture_size=lambda *x, ml=msg_label: setattr(ml, 'height', ml.texture_size[1])
            )
            messages_box.add_widget(msg_label)

        scroll.add_widget(messages_box)
        content.add_widget(scroll)

        # Bouton fermer
        close_btn = Button(
            text="Fermer",
            size_hint_y=None,
            height=dp(44),
            background_color=self.manager.app.theme['bg_secondary'],
            color=self.manager.app.theme['text_primary'],
            background_normal=''
        )

        popup = Popup(
            title="Résultats",
            content=content,
            size_hint=(0.9, 0.8),
            background_color=self.manager.app.theme['bg_primary']
        )

        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        popup.open()

    def _on_reset_db(self, *args):
        """Affiche une confirmation avant de réinitialiser"""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        content.add_widget(Label(
            text="Êtes-vous sûr de vouloir réinitialiser\nla base de données ?",
            font_size=dp(13),
            color=self.manager.app.theme['text_primary'],
            halign='center',
            size_hint_y=0.6
        ))

        content.add_widget(Label(
            text="Cette action supprimera tous les membres !",
            font_size=dp(11),
            color=self.manager.app.theme['error'],
            halign='center',
            size_hint_y=0.2
        ))

        button_box = BoxLayout(size_hint_y=0.2, spacing=dp(10))

        def on_confirm():
            self.manager.app.db.init_db()
            popup.dismiss()

        confirm_btn = Button(
            text="Réinitialiser",
            background_color=self.manager.app.theme['error'],
            color=(1, 1, 1, 1),
            background_normal=''
        )
        cancel_btn = Button(
            text="Annuler",
            background_color=self.manager.app.theme['bg_secondary'],
            color=self.manager.app.theme['text_primary'],
            background_normal=''
        )

        confirm_btn.bind(on_release=lambda x: on_confirm())
        cancel_btn.bind(on_release=lambda x: popup.dismiss())

        button_box.add_widget(confirm_btn)
        button_box.add_widget(cancel_btn)

        content.add_widget(button_box)

        popup = Popup(
            title="Confirmation",
            content=content,
            size_hint=(0.85, 0.5),
            background_color=self.manager.app.theme['bg_primary']
        )
        popup.open()

    def _on_about(self, *args):
        """Affiche le popup À propos"""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        content.add_widget(Label(
            text="[b]CENAD[/b]",
            markup=True,
            font_size=dp(18),
            bold=True,
            color=self.manager.app.theme['accent'],
            size_hint_y=None,
            height=dp(40)
        ))

        content.add_widget(Label(
            text="Communauté des Étudiants Natifs d'Andapa",
            font_size=dp(12),
            color=self.manager.app.theme['text_primary'],
            size_hint_y=None,
            height=dp(30)
        ))

        scroll = ScrollView(size_hint_y=0.6)
        info_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8), padding=dp(10))
        info_box.bind(minimum_height=info_box.setter('height'))

        info_list = [
            ("Version", "1.0.0"),
            ("Fondée", "2012"),
            ("Lieu", "Antsiranana, Madagascar"),
            ("Développeur", "CENAD Dev Team"),
            ("Framework", "Kivy 2.3.0"),
            ("Base de données", "SQLite"),
        ]

        for label, value in info_list:
            row = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(10))

            row.add_widget(Label(
                text=f"[b]{label}[/b]",
                markup=True,
                font_size=dp(11),
                color=self.manager.app.theme['accent'],
                size_hint_x=0.35
            ))

            row.add_widget(Label(
                text=value,
                font_size=dp(11),
                color=self.manager.app.theme['text_primary'],
                size_hint_x=0.65
            ))

            info_box.add_widget(row)

        scroll.add_widget(info_box)
        content.add_widget(scroll)

        close_btn = Button(
            text="Fermer",
            size_hint_y=None,
            height=dp(44),
            background_color=self.manager.app.theme['bg_secondary'],
            color=self.manager.app.theme['text_primary'],
            background_normal=''
        )

        popup = Popup(
            title="À propos",
            content=content,
            size_hint=(0.9, 0.8),
            background_color=self.manager.app.theme['bg_primary']
        )

        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        popup.open()

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos
