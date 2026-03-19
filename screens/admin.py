"""
screens/admin.py - Administration CRUD sécurisée par SHA-256
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
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
import db_manager as db


def make_bg(widget, r, g, b, a=1):
    with widget.canvas.before:
        Color(r, g, b, a)
        rect = Rectangle(size=widget.size, pos=widget.pos)
    widget.bind(size=lambda *x: setattr(rect, 'size', widget.size),
                pos=lambda *x: setattr(rect, 'pos', widget.pos))
    return rect


class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.authenticated = False
        self._built = False

    def on_enter(self):
        if not self._built:
            self._build_login()
            self._built = True

    def _build_login(self):
        make_bg(self, 0.05, 0.07, 0.25, 1)
        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))

        layout.add_widget(Label(text="[b]🔐 ADMINISTRATION[/b]", markup=True,
                                 font_size=dp(20), color=(1, 0.85, 0.1, 1),
                                 size_hint_y=None, height=dp(50)))
        layout.add_widget(Label(text="Mot de passe requis", font_size=dp(14),
                                 color=(0.7, 0.8, 1, 1), size_hint_y=None, height=dp(30)))

        self.pwd_input = TextInput(
            hint_text="Entrez le mot de passe...",
            password=True, multiline=False,
            size_hint_y=None, height=dp(50),
            background_color=(0.15, 0.2, 0.45, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.6, 0.8, 1),
            cursor_color=(1, 1, 1, 1),
            font_size=dp(14)
        )
        layout.add_widget(self.pwd_input)

        login_btn = Button(text="Se connecter", size_hint_y=None, height=dp(50),
                           background_color=(0.13, 0.55, 0.13, 1), background_normal='',
                           font_size=dp(15), color=(1, 1, 1, 1))
        login_btn.bind(on_release=self._check_password)
        layout.add_widget(login_btn)

        back_btn = Button(text="◀ Retour", size_hint_y=None, height=dp(44),
                          background_color=(0.3, 0.3, 0.5, 1), background_normal='',
                          font_size=dp(13), color=(1, 1, 1, 1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        layout.add_widget(back_btn)

        self.error_label = Label(text="", color=(1, 0.3, 0.3, 1),
                                  size_hint_y=None, height=dp(30))
        layout.add_widget(self.error_label)

        layout.add_widget(Label())  # spacer
        self.add_widget(layout)

    def _check_password(self, *args):
        pwd = self.pwd_input.text
        if db.verify_admin_password(pwd):
            self.authenticated = True
            self.clear_widgets()
            self._build_admin_panel()
        else:
            self.error_label.text = "❌ Mot de passe incorrect"
            self.pwd_input.text = ""

    def _build_admin_panel(self):
        make_bg(self, 0.05, 0.07, 0.25, 1)
        main = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = Button(text="◀", size_hint=(None, 1), width=dp(40),
                          background_color=(0.2, 0.3, 0.7, 1), background_normal='')
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        header.add_widget(back_btn)
        header.add_widget(Label(text="[b]🔐 ADMINISTRATION[/b]", markup=True,
                                 font_size=dp(15), color=(1, 0.85, 0.1, 1)))
        add_btn = Button(text="➕ Ajouter", size_hint=(None, 1), width=dp(110),
                         background_color=(0.13, 0.55, 0.13, 1), background_normal='',
                         font_size=dp(13), color=(1, 1, 1, 1))
        add_btn.bind(on_release=lambda x: self._open_form())
        header.add_widget(add_btn)
        main.add_widget(header)

        # Liste membres
        scroll = ScrollView()
        self.member_list = BoxLayout(orientation='vertical', spacing=dp(4),
                                     size_hint_y=None, padding=(0, dp(4)))
        self.member_list.bind(minimum_height=self.member_list.setter('height'))
        scroll.add_widget(self.member_list)
        main.add_widget(scroll)

        self.add_widget(main)
        self._load_list()

    def _load_list(self):
        self.member_list.clear_widgets()
        membres = db.get_all_membres()
        for m in membres:
            row = AdminMemberRow(m, self._edit_membre, self._delete_membre)
            self.member_list.add_widget(row)

    def _open_form(self, membre=None):
        """Ouvre un popup formulaire pour ajouter/modifier."""
        popup = MemberFormPopup(membre, on_save=self._on_save)
        popup.open()

    def _edit_membre(self, membre_id):
        m = db.get_membre_by_id(membre_id)
        self._open_form(m)

    def _delete_membre(self, membre_id, nom):
        def confirm(*a):
            db.delete_membre(membre_id)
            self._load_list()
            popup.dismiss()

        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(text=f"Supprimer [b]{nom}[/b] ?", markup=True,
                                  color=(1, 1, 1, 1), font_size=dp(14)))
        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        confirm_btn = Button(text="Supprimer", background_color=(0.8, 0.1, 0.1, 1),
                              background_normal='', color=(1, 1, 1, 1))
        cancel_btn = Button(text="Annuler", background_color=(0.3, 0.3, 0.5, 1),
                             background_normal='', color=(1, 1, 1, 1))
        confirm_btn.bind(on_release=confirm)
        btns.add_widget(confirm_btn)
        btns.add_widget(cancel_btn)
        content.add_widget(btns)
        popup = Popup(title="Confirmation", content=content,
                      size_hint=(0.85, 0.35),
                      background_color=(0.1, 0.15, 0.4, 1))
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def _on_save(self, data, membre_id=None):
        if membre_id:
            db.update_membre(membre_id, data)
        else:
            db.add_membre(data)
        self._load_list()


class AdminMemberRow(BoxLayout):
    def __init__(self, membre, edit_cb, delete_cb, **kwargs):
        super().__init__(size_hint_y=None, height=dp(52), spacing=dp(5),
                          padding=(dp(5), 0), **kwargs)
        make_bg(self, 0.1, 0.15, 0.4, 0.6)

        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(text=membre['nom'], font_size=dp(13),
                               color=(1, 1, 1, 1), halign='left',
                               text_size=(dp(170), None)))
        info.add_widget(Label(
            text=f"{membre.get('niveau','')} | {membre.get('batiment','')} | {membre.get('etablissement','')}",
            font_size=dp(10), color=(0.6, 0.8, 1, 0.8), halign='left',
            text_size=(dp(170), None)
        ))
        self.add_widget(info)

        edit_btn = Button(text="✏", size_hint=(None, 1), width=dp(40),
                          background_color=(0.15, 0.5, 0.85, 1), background_normal='',
                          font_size=dp(15), color=(1, 1, 1, 1))
        edit_btn.bind(on_release=lambda x: edit_cb(membre['id']))

        del_btn = Button(text="🗑", size_hint=(None, 1), width=dp(40),
                          background_color=(0.75, 0.1, 0.1, 1), background_normal='',
                          font_size=dp(15), color=(1, 1, 1, 1))
        del_btn.bind(on_release=lambda x: delete_cb(membre['id'], membre['nom']))

        self.add_widget(edit_btn)
        self.add_widget(del_btn)


class MemberFormPopup(Popup):
    NIVEAUX = ["L1", "L2", "L3", "M1", "M2"]
    BATIMENTS = ["Bâtiment A", "Bâtiment B", "Bâtiment C", "Bâtiment D", "Bâtiment E"]
    ETABLISSEMENTS = ["ENSET", "ESP", "AGRO", "SCIENCES", "FLSH", "DEGSP", "ISAE", "IST", "ISISFA", "Autre"]

    def __init__(self, membre=None, on_save=None, **kwargs):
        self.membre = membre
        self.on_save_cb = on_save

        content = self._build_form()
        super().__init__(
            title="Modifier membre" if membre else "Ajouter un membre",
            content=content,
            size_hint=(0.95, 0.90),
            background_color=(0.07, 0.10, 0.30, 1),
            **kwargs
        )

    def _build_form(self):
        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing=dp(8), padding=dp(10),
                            size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        m = self.membre or {}

        def field(hint, key, default=''):
            inp = TextInput(
                hint_text=hint, text=str(m.get(key, default)),
                multiline=False, size_hint_y=None, height=dp(44),
                background_color=(0.15, 0.2, 0.45, 1),
                foreground_color=(1, 1, 1, 1),
                hint_text_color=(0.5, 0.6, 0.8, 1),
                cursor_color=(1, 1, 1, 1), font_size=dp(13)
            )
            return inp

        self.nom_input = field("Nom complet *", 'nom')
        self.telephone_input = field("Téléphone", 'telephone')
        self.commune_input = field("Commune d'origine", 'commune_origine')

        self.sexe_spinner = Spinner(text=m.get('sexe', 'M'), values=['M', 'F'],
                                     size_hint_y=None, height=dp(44),
                                     background_color=(0.2, 0.3, 0.7, 1),
                                     color=(1, 1, 1, 1))
        self.niveau_spinner = Spinner(text=m.get('niveau', 'L1'), values=self.NIVEAUX,
                                       size_hint_y=None, height=dp(44),
                                       background_color=(0.2, 0.3, 0.7, 1),
                                       color=(1, 1, 1, 1))
        self.promotion_input = field("Promotion (ex: 2022)", 'promotion')
        self.batiment_spinner = Spinner(
            text=m.get('batiment', 'Bâtiment A'), values=self.BATIMENTS,
            size_hint_y=None, height=dp(44),
            background_color=(0.2, 0.3, 0.7, 1), color=(1, 1, 1, 1)
        )
        self.etab_spinner = Spinner(
            text=m.get('etablissement', 'ENSET'), values=self.ETABLISSEMENTS,
            size_hint_y=None, height=dp(44),
            background_color=(0.2, 0.3, 0.7, 1), color=(1, 1, 1, 1)
        )

        def lbl(text):
            return Label(text=text, color=(0.7, 0.85, 1, 1), size_hint_y=None,
                          height=dp(22), halign='left', font_size=dp(12))

        for w, hint in [
            (lbl("Nom complet *"), None),
            (self.nom_input, None),
            (lbl("Sexe"), None),
            (self.sexe_spinner, None),
            (lbl("Niveau"), None),
            (self.niveau_spinner, None),
            (lbl("Promotion"), None),
            (self.promotion_input, None),
            (lbl("Bâtiment"), None),
            (self.batiment_spinner, None),
            (lbl("Établissement"), None),
            (self.etab_spinner, None),
            (lbl("Téléphone"), None),
            (self.telephone_input, None),
            (lbl("Commune d'origine"), None),
            (self.commune_input, None),
        ]:
            layout.add_widget(w)

        # Boutons
        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        save_btn = Button(text="💾 Enregistrer",
                          background_color=(0.13, 0.55, 0.13, 1), background_normal='',
                          color=(1, 1, 1, 1), font_size=dp(14))
        cancel_btn = Button(text="Annuler",
                            background_color=(0.4, 0.1, 0.1, 1), background_normal='',
                            color=(1, 1, 1, 1), font_size=dp(14))
        save_btn.bind(on_release=self._save)
        cancel_btn.bind(on_release=self.dismiss)
        btns.add_widget(save_btn)
        btns.add_widget(cancel_btn)
        layout.add_widget(btns)

        scroll.add_widget(layout)
        return scroll

    def _save(self, *args):
        nom = self.nom_input.text.strip()
        if not nom:
            return
        data = {
            'nom': nom,
            'sexe': self.sexe_spinner.text,
            'niveau': self.niveau_spinner.text,
            'promotion': self.promotion_input.text.strip(),
            'batiment': self.batiment_spinner.text,
            'etablissement': self.etab_spinner.text,
            'commune_origine': self.commune_input.text.strip(),
            'telephone': self.telephone_input.text.strip(),
            'photo': self.membre.get('photo', '') if self.membre else ''
        }
        if self.on_save_cb:
            membre_id = self.membre['id'] if self.membre else None
            self.on_save_cb(data, membre_id)
        self.dismiss()
