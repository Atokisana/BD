"""
screens/admin.py - Administration CRUD securisee par SHA-256
Amelioration: recherche, batiments dynamiques, validation, toast
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
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
import db_manager as db


def make_bg(widget, r, g, b, a=1, radius=0):
    with widget.canvas.before:
        Color(r, g, b, a)
        if radius:
            rect = RoundedRectangle(size=widget.size, pos=widget.pos, radius=[dp(radius)])
        else:
            rect = Rectangle(size=widget.size, pos=widget.pos)
    widget.bind(size=lambda *x: setattr(rect, 'size', widget.size),
                pos=lambda *x: setattr(rect, 'pos', widget.pos))
    return rect


class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.authenticated = False
        self._built = False
        self._search_event = None

    def on_enter(self):
        if not self._built:
            self._build_login()
            self._built = True

    def _build_login(self):
        make_bg(self, 0.05, 0.07, 0.25, 1)
        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))

        layout.add_widget(Label(text="[b]ADMINISTRATION[/b]", markup=True,
                                 font_size=dp(20), color=(1, 0.85, 0.1, 1),
                                 size_hint_y=None, height=dp(50)))
        layout.add_widget(Label(text="Mot de passe requis", font_size=dp(14),
                                 color=(0.7, 0.8, 1, 1), size_hint_y=None, height=dp(30)))

        self.pwd_input = TextInput(
            hint_text="Entrez le mot de passe...",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            background_color=(0.15, 0.2, 0.45, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.6, 0.8, 1),
            cursor_color=(1, 1, 1, 1),
            font_size=dp(14),
            write_tab=False,
        )
        layout.add_widget(self.pwd_input)

        login_btn = Button(text="Se connecter", size_hint_y=None, height=dp(50),
                           background_color=(0.13, 0.55, 0.13, 1),
                           font_size=dp(15), color=(1, 1, 1, 1))
        login_btn.bind(on_release=self._check_password)
        layout.add_widget(login_btn)

        back_btn = Button(text="< Retour", size_hint_y=None, height=dp(44),
                          background_color=(0.3, 0.3, 0.5, 1),
                          font_size=dp(13), color=(1, 1, 1, 1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        layout.add_widget(back_btn)

        self.error_label = Label(text="", color=(1, 0.3, 0.3, 1),
                                  size_hint_y=None, height=dp(30))
        layout.add_widget(self.error_label)
        layout.add_widget(Label())
        self.add_widget(layout)

    def _check_password(self, *args):
        pwd = self.pwd_input.text
        if db.verify_admin_password(pwd):
            self.authenticated = True
            self.clear_widgets()
            self._build_admin_panel()
        else:
            self.error_label.text = "Mot de passe incorrect"
            self.pwd_input.text = ""

    def _build_admin_panel(self):
        make_bg(self, 0.05, 0.07, 0.25, 1)
        main = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        back_btn = Button(text="<", size_hint=(None, 1), width=dp(44),
                          background_color=(0.2, 0.3, 0.7, 1),
                          font_size=dp(18), color=(1, 1, 1, 1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        header.add_widget(back_btn)
        header.add_widget(Label(text="[b]ADMINISTRATION[/b]", markup=True,
                                 font_size=dp(15), color=(1, 0.85, 0.1, 1)))
        add_btn = Button(text="+ Ajouter", size_hint=(None, 1), width=dp(100),
                         background_color=(0.13, 0.55, 0.13, 1),
                         font_size=dp(13), color=(1, 1, 1, 1))
        add_btn.bind(on_release=lambda x: self._open_form())
        header.add_widget(add_btn)
        main.add_widget(header)

        # Search bar in admin
        search_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        self.admin_search = TextInput(
            hint_text="Rechercher...",
            multiline=False,
            size_hint=(1, 1),
            background_color=(0.12, 0.16, 0.40, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.6, 0.8, 1),
            cursor_color=(1, 1, 1, 1),
            font_size=dp(12)
        )
        self.admin_search.bind(text=self._on_admin_search)
        search_box.add_widget(self.admin_search)

        # Member count
        self.count_label = Label(text="0", size_hint=(None, 1), width=dp(50),
                                  font_size=dp(12), color=(1, 0.85, 0.1, 1), bold=True)
        search_box.add_widget(self.count_label)
        main.add_widget(search_box)

        scroll = ScrollView()
        self.member_list = BoxLayout(orientation='vertical', spacing=dp(4),
                                     size_hint_y=None, padding=(0, dp(4)))
        self.member_list.bind(minimum_height=self.member_list.setter('height'))
        scroll.add_widget(self.member_list)
        main.add_widget(scroll)

        self.add_widget(main)
        self._load_list()

    def _on_admin_search(self, instance, value):
        if self._search_event:
            self._search_event.cancel()
        self._search_event = Clock.schedule_once(lambda dt: self._load_list(), 0.4)

    def _load_list(self):
        self.member_list.clear_widgets()
        search_text = ""
        if hasattr(self, 'admin_search'):
            search_text = self.admin_search.text.strip()

        if search_text:
            membres = db.search_membres(query=search_text)
        else:
            membres = db.get_all_membres()

        self.count_label.text = str(len(membres))

        for m in membres:
            row = AdminMemberRow(m, self._edit_membre, self._delete_membre)
            self.member_list.add_widget(row)

    def _open_form(self, membre=None):
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
            try:
                from toast import show_toast
                show_toast(f"Membre supprime", bg_color=(0.75, 0.1, 0.1, 0.92))
            except Exception:
                pass

        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(text="Supprimer [b]{}[/b] ?".format(nom), markup=True,
                                  color=(1, 1, 1, 1), font_size=dp(14)))
        btns = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        confirm_btn = Button(text="Supprimer", background_color=(0.8, 0.1, 0.1, 1),
                              color=(1, 1, 1, 1))
        cancel_btn = Button(text="Annuler", background_color=(0.3, 0.3, 0.5, 1),
                             color=(1, 1, 1, 1))
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
            action = "modifie"
        else:
            db.add_membre(data)
            action = "ajoute"
        self._load_list()
        try:
            from toast import show_toast
            show_toast(f"Membre {action} avec succes")
        except Exception:
            pass


class AdminMemberRow(BoxLayout):
    def __init__(self, membre, edit_cb, delete_cb, **kwargs):
        super().__init__(size_hint_y=None, height=dp(56), spacing=dp(5),
                          padding=(dp(8), dp(4)), **kwargs)
        make_bg(self, 0.10, 0.14, 0.38, 0.6, radius=8)

        # Avatar
        sexe_color = (0.25, 0.60, 1.00, 1) if membre.get('sexe') == 'M' else (0.90, 0.30, 0.55, 1)
        sexe_letter = "M" if membre.get('sexe') == 'M' else "F"
        self.add_widget(Label(text=sexe_letter, size_hint=(None, 1), width=dp(30),
                               font_size=dp(15), color=sexe_color, bold=True))

        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(text=membre['nom'], font_size=dp(13),
                               color=(1, 1, 1, 1), halign='left',
                               text_size=(dp(150), None), bold=True))
        info.add_widget(Label(
            text="{} | {} | {}".format(
                membre.get('niveau', ''),
                membre.get('batiment', ''),
                membre.get('etablissement', '')
            ),
            font_size=dp(10), color=(0.6, 0.8, 1, 0.8), halign='left',
            text_size=(dp(150), None)
        ))
        self.add_widget(info)

        edit_btn = Button(text="Edit", size_hint=(None, 1), width=dp(48),
                          background_color=(0.15, 0.5, 0.85, 1),
                          font_size=dp(11), color=(1, 1, 1, 1))
        edit_btn.bind(on_release=lambda x: edit_cb(membre['id']))

        del_btn = Button(text="X", size_hint=(None, 1), width=dp(40),
                          background_color=(0.75, 0.1, 0.1, 1),
                          font_size=dp(13), color=(1, 1, 1, 1))
        del_btn.bind(on_release=lambda x: delete_cb(membre['id'], membre['nom']))

        self.add_widget(edit_btn)
        self.add_widget(del_btn)


class MemberFormPopup(Popup):
    NIVEAUX = ["L1", "L2", "L3", "M1", "M2"]
    ETABLISSEMENTS = ["ENSET", "ESP", "AGRO", "SCIENCES", "FLSH", "DEGSP", "ISAE", "IST", "ISISFA"]

    def __init__(self, membre=None, on_save=None, **kwargs):
        self.membre = membre
        self.on_save_cb = on_save
        content = self._build_form()
        super().__init__(
            title="Modifier" if membre else "Ajouter un membre",
            content=content,
            size_hint=(0.95, 0.90),
            background_color=(0.07, 0.10, 0.30, 1),
            **kwargs
        )

    def _build_form(self):
        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing=dp(8), padding=dp(12), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        m = self.membre or {}

        def field(hint, key):
            return TextInput(
                hint_text=hint, text=str(m.get(key, '')),
                multiline=False, size_hint_y=None, height=dp(44),
                background_color=(0.15, 0.2, 0.45, 1),
                foreground_color=(1, 1, 1, 1),
                hint_text_color=(0.5, 0.6, 0.8, 1),
                cursor_color=(1, 1, 1, 1),
                font_size=dp(13),
                write_tab=False,
            )

        def lbl(text):
            return Label(text=text, color=(0.7, 0.85, 1, 1), size_hint_y=None,
                          height=dp(22), halign='left', font_size=dp(12))

        self.nom_input = field("Nom complet *", 'nom')
        self.telephone_input = field("Telephone", 'telephone')
        self.commune_input = field("Commune d'origine", 'commune_origine')
        self.promotion_input = field("Promotion (ex: 2022)", 'promotion')
        self.batiment_input = field("Batiment (ex: BLOC A)", 'batiment')

        self.sexe_spinner = Spinner(text=m.get('sexe', 'M'), values=['M', 'F'],
                                     size_hint_y=None, height=dp(44),
                                     background_color=(0.2, 0.3, 0.7, 1), color=(1, 1, 1, 1))
        self.niveau_spinner = Spinner(text=m.get('niveau', 'L1'), values=self.NIVEAUX,
                                       size_hint_y=None, height=dp(44),
                                       background_color=(0.2, 0.3, 0.7, 1), color=(1, 1, 1, 1))
        self.etab_spinner = Spinner(text=m.get('etablissement', 'ENSET'), values=self.ETABLISSEMENTS,
                                     size_hint_y=None, height=dp(44),
                                     background_color=(0.2, 0.3, 0.7, 1), color=(1, 1, 1, 1))

        # Validation label
        self.validation_label = Label(text="", color=(1, 0.3, 0.3, 1),
                                       size_hint_y=None, height=dp(22), font_size=dp(11))

        widgets = [
            lbl("Nom complet *"), self.nom_input,
            lbl("Sexe"), self.sexe_spinner,
            lbl("Niveau"), self.niveau_spinner,
            lbl("Promotion"), self.promotion_input,
            lbl("Batiment"), self.batiment_input,
            lbl("Etablissement"), self.etab_spinner,
            lbl("Telephone"), self.telephone_input,
            lbl("Commune d'origine"), self.commune_input,
            self.validation_label,
        ]
        for w in widgets:
            layout.add_widget(w)

        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        save_btn = Button(text="Enregistrer",
                          background_color=(0.13, 0.55, 0.13, 1),
                          color=(1, 1, 1, 1), font_size=dp(14))
        cancel_btn = Button(text="Annuler",
                            background_color=(0.4, 0.1, 0.1, 1),
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
            self.validation_label.text = "Le nom est obligatoire"
            return

        telephone = self.telephone_input.text.strip()
        if telephone and not telephone.replace('+', '').replace(' ', '').isdigit():
            self.validation_label.text = "Telephone invalide"
            return

        data = {
            'nom': nom,
            'sexe': self.sexe_spinner.text,
            'niveau': self.niveau_spinner.text,
            'promotion': self.promotion_input.text.strip(),
            'batiment': self.batiment_input.text.strip(),
            'etablissement': self.etab_spinner.text,
            'commune_origine': self.commune_input.text.strip(),
            'telephone': telephone,
            'photo': self.membre.get('photo', '') if self.membre else ''
        }
        if self.on_save_cb:
            membre_id = self.membre['id'] if self.membre else None
            self.on_save_cb(data, membre_id)
        self.dismiss()
